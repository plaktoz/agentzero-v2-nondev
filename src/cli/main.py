"""
CLI interface for Unified Content Agent System.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown
import yaml
import structlog

from ..core.coordinator import Coordinator
from ..providers.claude import ClaudeProvider
from ..storage.documents import DocumentStorage

app = typer.Typer(
    name="ucas",
    help="Unified Content Agent System - Multi-agent content creation",
    add_completion=False
)

console = Console()
logger = structlog.get_logger()


def load_config() -> dict:
    """Load system configuration."""
    config_file = Path("config/default.yaml")
    
    if not config_file.exists():
        console.print("[yellow]Warning: config/default.yaml not found, using defaults[/yellow]")
        return {
            "system": {"max_agents": 5, "default_provider": "claude"},
            "providers": {
                "claude": {
                    "enabled": True,
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "api_key_env": "ANTHROPIC_API_KEY"
                }
            },
            "storage": {"documents_path": "./documents"}
        }
    
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def get_coordinator() -> Coordinator:
    """Initialize and return coordinator."""
    config = load_config()
    
    # Initialize provider
    provider_config = config["providers"]["claude"]
    provider = ClaudeProvider(provider_config)
    
    # Initialize storage
    storage_path = config["storage"]["documents_path"]
    storage = DocumentStorage(storage_path)
    
    # Initialize coordinator
    coordinator = Coordinator(provider, storage, config)
    
    return coordinator


@app.command()
def init():
    """Initialize the system."""
    console.print(Panel.fit(
        "[bold blue]Unified Content Agent System[/bold blue]\n"
        "Initializing...",
        border_style="blue"
    ))
    
    # Create directories
    directories = [
        "config",
        "documents/research",
        "documents/drafts",
        "documents/finals",
        "documents/metadata",
        "logs",
        "metrics"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        console.print(f"✓ Created directory: {directory}")
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("\n[yellow]⚠ Warning: ANTHROPIC_API_KEY not set[/yellow]")
        console.print("Set your API key: export ANTHROPIC_API_KEY=your_key_here")
    else:
        console.print("\n✓ API key configured")
    
    console.print("\n[green]✓ System initialized successfully![/green]")
    console.print("\nNext steps:")
    console.print("  1. Set API key if not already set")
    console.print("  2. Run: ucas request \"Write a blog post about AI\"")
    console.print("  3. Check status: ucas status <request-id>")


@app.command()
def request(
    description: str = typer.Argument(..., help="Description of content to create"),
    content_type: Optional[str] = typer.Option(None, "--type", "-t", help="Content type (blog_post, research_report, etc.)"),
    word_count: Optional[int] = typer.Option(None, "--words", "-w", help="Target word count"),
):
    """Submit a content creation request."""
    
    async def _request():
        coordinator = get_coordinator()
        
        # Build requirements
        requirements = {}
        if word_count:
            requirements["target_words"] = word_count
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing request...", total=None)
            
            try:
                request_id = await coordinator.request(
                    description=description,
                    content_type=content_type,
                    **requirements
                )
                
                progress.update(task, description="[green]Request submitted![/green]")
                
                console.print(f"\n[green]✓ Request submitted successfully![/green]")
                console.print(f"Request ID: [bold]{request_id}[/bold]")
                console.print(f"\nCheck status: ucas status {request_id}")
                console.print(f"View content: ucas show {request_id}")
                
            except Exception as e:
                progress.update(task, description="[red]Request failed[/red]")
                console.print(f"\n[red]✗ Error: {str(e)}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(_request())


@app.command()
def status(
    request_id: str = typer.Argument(..., help="Request ID to check")
):
    """Check status of a content request."""
    
    async def _status():
        coordinator = get_coordinator()
        
        try:
            status_info = await coordinator.get_status(request_id)
            
            if status_info["status"] == "not_found":
                console.print(f"[red]✗ Request not found: {request_id}[/red]")
                raise typer.Exit(1)
            
            # Create status table
            table = Table(title=f"Request Status: {request_id}")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Workflow", status_info["workflow"])
            table.add_row("Status", status_info["status"])
            table.add_row("Progress", f"{status_info['current_step']}/{status_info['total_steps']}")
            table.add_row("Completed Steps", ", ".join(status_info["completed_steps"]))
            table.add_row("Total Tokens", str(status_info["total_tokens"]))
            
            if status_info.get("error"):
                table.add_row("Error", f"[red]{status_info['error']}[/red]")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_status())


@app.command()
def show(
    request_id: str = typer.Argument(..., help="Request ID to show"),
    version: Optional[int] = typer.Option(None, "--version", "-v", help="Specific version to show")
):
    """Show content for a request."""
    
    async def _show():
        coordinator = get_coordinator()
        
        try:
            content, metadata = await coordinator.storage.load_document(request_id, version)
            
            # Display metadata
            console.print(Panel(
                f"[bold]{metadata.title}[/bold]\n"
                f"Type: {metadata.content_type}\n"
                f"Status: {metadata.status}\n"
                f"Version: {metadata.version}\n"
                f"Words: {metadata.word_count}\n"
                f"Updated: {metadata.updated_at}",
                title="Document Info",
                border_style="blue"
            ))
            
            # Display content
            console.print("\n")
            md = Markdown(content)
            console.print(md)
            
        except FileNotFoundError:
            console.print(f"[red]✗ Document not found: {request_id}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_show())


@app.command()
def list(
    status_filter: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    content_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by content type")
):
    """List all documents."""
    
    async def _list():
        coordinator = get_coordinator()
        
        try:
            documents = await coordinator.storage.list_documents(
                status=status_filter,
                content_type=content_type
            )
            
            if not documents:
                console.print("[yellow]No documents found[/yellow]")
                return
            
            # Create table
            table = Table(title="Documents")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white")
            table.add_column("Type", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Words", justify="right")
            table.add_column("Updated", style="blue")
            
            for doc in documents:
                table.add_row(
                    doc.id[:8] + "...",
                    doc.title[:40] + "..." if len(doc.title) > 40 else doc.title,
                    doc.content_type,
                    doc.status,
                    str(doc.word_count),
                    doc.updated_at[:10]
                )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_list())


@app.command()
def approve(
    request_id: str = typer.Argument(..., help="Request ID to approve")
):
    """Approve content for publishing."""
    
    async def _approve():
        coordinator = get_coordinator()
        
        try:
            await coordinator.storage.update_status(request_id, "approved")
            console.print(f"[green]✓ Content approved: {request_id}[/green]")
            
        except FileNotFoundError:
            console.print(f"[red]✗ Document not found: {request_id}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_approve())


@app.command()
def workflows():
    """List available workflows."""
    coordinator = get_coordinator()
    
    workflows_list = coordinator.router.list_workflows()
    
    table = Table(title="Available Workflows")
    table.add_column("Content Type", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Description", style="green")
    table.add_column("Agents", style="yellow")
    table.add_column("Steps", justify="right")
    
    for workflow in workflows_list:
        table.add_row(
            workflow["content_type"],
            workflow["name"],
            workflow["description"],
            ", ".join(workflow["agents"]),
            str(workflow["steps"])
        )
    
    console.print(table)


@app.command()
def update(
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Create backup before update"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update without confirmation")
):
    """Update the system to the latest version."""
    
    console.print(Panel.fit(
        "[bold blue]System Update[/bold blue]\n"
        "Checking for updates...",
        border_style="blue"
    ))
    
    # Check current version
    config = load_config()
    current_version = config.get("system", {}).get("version", "0.1.0")
    console.print(f"Current version: [cyan]{current_version}[/cyan]")
    
    # In production, this would check for updates from a remote source
    console.print("\n[yellow]Update feature coming in Phase 2[/yellow]")
    console.print("This will support:")
    console.print("  • In-place updates without data loss")
    console.print("  • Automatic backup creation")
    console.print("  • Configuration preservation")
    console.print("  • Rollback capability")
    
    if backup:
        console.print("\n[green]✓ Backup would be created at: ./backups/[/green]")
    
    console.print("\n[blue]For now, update manually:[/blue]")
    console.print("  1. git pull origin main")
    console.print("  2. pip install -r requirements.txt --upgrade")
    console.print("  3. ucas init  # Re-initialize if needed")


@app.command()
def uninstall(
    keep_data: bool = typer.Option(True, "--keep-data/--remove-data", help="Keep user data"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Uninstall the system."""
    
    if not force:
        confirm = typer.confirm(
            "Are you sure you want to uninstall? This will remove system files."
        )
        if not confirm:
            console.print("[yellow]Uninstall cancelled[/yellow]")
            raise typer.Exit(0)
    
    console.print(Panel.fit(
        "[bold red]System Uninstall[/bold red]\n"
        "Removing system files...",
        border_style="red"
    ))
    
    # Directories to remove
    system_dirs = ["logs", "metrics"]
    if not keep_data:
        system_dirs.extend(["documents", "knowledge_base", "research"])
    
    removed_count = 0
    for directory in system_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            import shutil
            shutil.rmtree(dir_path)
            console.print(f"✓ Removed: {directory}")
            removed_count += 1
    
    if keep_data:
        console.print("\n[green]✓ User data preserved in:[/green]")
        console.print("  • documents/")
        console.print("  • config/")
    else:
        console.print("\n[yellow]⚠ All data removed[/yellow]")
    
    console.print(f"\n[green]✓ Uninstall complete ({removed_count} directories removed)[/green]")
    console.print("\nTo reinstall:")
    console.print("  pip install -e .")
    console.print("  ucas init")


@app.command()
def rollback(
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version to rollback to"),
    list_versions: bool = typer.Option(False, "--list", "-l", help="List available versions")
):
    """Rollback to a previous version."""
    
    if list_versions:
        console.print(Panel.fit(
            "[bold blue]Available Versions[/bold blue]",
            border_style="blue"
        ))
        
        # In production, this would list actual backup versions
        console.print("\n[yellow]Rollback feature coming in Phase 2[/yellow]")
        console.print("This will support:")
        console.print("  • List all backup versions")
        console.print("  • Rollback to specific version")
        console.print("  • Preserve user data during rollback")
        console.print("  • Automatic configuration migration")
        
        console.print("\n[blue]Example versions:[/blue]")
        console.print("  • 0.1.0 (current)")
        console.print("  • 0.0.9 (2024-01-15)")
        console.print("  • 0.0.8 (2024-01-10)")
        return
    
    if not version:
        console.print("[red]✗ Please specify a version with --version[/red]")
        console.print("Use --list to see available versions")
        raise typer.Exit(1)
    
    console.print(f"[yellow]Rollback to version {version} coming in Phase 2[/yellow]")
    console.print("\nFor now, manually rollback:")
    console.print(f"  1. git checkout v{version}")
    console.print("  2. pip install -r requirements.txt")
    console.print("  3. ucas init")





if __name__ == "__main__":
    app()
