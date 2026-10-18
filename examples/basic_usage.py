"""
Basic usage example for Unified Content Agent System.
Demonstrates how to create content programmatically.
"""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.coordinator import Coordinator
from src.providers.claude import ClaudeProvider
from src.storage.documents import DocumentStorage


async def main():
    """Run basic usage example."""
    
    print("=" * 60)
    print("Unified Content Agent System - Basic Usage Example")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing system...")
    
    # Provider configuration
    provider_config = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "temperature": 0.7,
        "api_key_env": "ANTHROPIC_API_KEY"
    }
    
    provider = ClaudeProvider(provider_config)
    print(f"   ✓ Provider initialized: {provider.get_model_name()}")
    
    # Storage
    storage = DocumentStorage("./documents")
    print("   ✓ Storage initialized")
    
    # Coordinator
    config = {
        "system": {"max_agents": 5},
        "providers": {"claude": provider_config}
    }
    coordinator = Coordinator(provider, storage, config)
    print("   ✓ Coordinator initialized")
    
    # Submit content request
    print("\n2. Submitting content request...")
    request_id = await coordinator.request(
        description="Write a blog post about the benefits of AI in education",
        content_type="blog_post",
        target_words=800
    )
    print(f"   ✓ Request submitted: {request_id}")
    
    # Wait for completion (in real usage, this would be async)
    print("\n3. Waiting for workflow to complete...")
    print("   (This may take 1-2 minutes)")
    
    # Poll for status
    max_wait = 120  # 2 minutes
    waited = 0
    while waited < max_wait:
        await asyncio.sleep(5)
        waited += 5
        
        status = await coordinator.get_status(request_id)
        
        if status["status"] == "completed":
            print(f"   ✓ Workflow completed!")
            print(f"   - Steps: {', '.join(status['completed_steps'])}")
            print(f"   - Total tokens: {status['total_tokens']}")
            break
        elif status["status"] == "failed":
            print(f"   ✗ Workflow failed: {status.get('error')}")
            return
        else:
            print(f"   ⏳ Progress: {status['current_step']}/{status['total_steps']} steps")
    
    # Load and display document
    print("\n4. Loading document...")
    content, metadata = await storage.load_document(request_id)
    
    print(f"   ✓ Document loaded")
    print(f"   - Title: {metadata.title}")
    print(f"   - Type: {metadata.content_type}")
    print(f"   - Status: {metadata.status}")
    print(f"   - Word count: {metadata.word_count}")
    print(f"   - Version: {metadata.version}")
    
    # Display content preview
    print("\n5. Content preview:")
    print("-" * 60)
    lines = content.split("\n")
    preview_lines = lines[:20]  # First 20 lines
    print("\n".join(preview_lines))
    if len(lines) > 20:
        print(f"\n... ({len(lines) - 20} more lines)")
    print("-" * 60)
    
    print("\n✓ Example completed successfully!")
    print(f"\nFull content saved to: documents/drafts/{request_id}/v1.md")
    print(f"Metadata saved to: documents/metadata/{request_id}.json")


if __name__ == "__main__":
    asyncio.run(main())
