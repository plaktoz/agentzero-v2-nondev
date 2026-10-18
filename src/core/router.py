"""
Router - Workflow selection and routing based on content type.
Maps content types to appropriate workflows and agents.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class Router:
    """
    Routes content requests to appropriate workflows.
    Loads workflow definitions and selects agents for each step.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize router.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.workflows = self._load_workflows()
        
        logger.info("router_initialized", workflow_count=len(self.workflows))
    
    def _load_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Load workflow definitions from config file.
        
        Returns:
            Dictionary of workflows keyed by content type
        """
        # Try to load from config/workflows.yaml
        workflow_file = Path("config/workflows.yaml")
        
        if not workflow_file.exists():
            logger.warning("workflows_file_not_found", using_defaults=True)
            return self._get_default_workflows()
        
        try:
            with open(workflow_file, "r") as f:
                data = yaml.safe_load(f)
                workflows = data.get("workflows", {})
                
            logger.info("workflows_loaded", count=len(workflows))
            return workflows
            
        except Exception as e:
            logger.error("workflows_load_failed", error=str(e), using_defaults=True)
            return self._get_default_workflows()
    
    def _get_default_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Get default workflow definitions.
        
        Returns:
            Default workflows
        """
        return {
            "blog_post": {
                "name": "Blog Post",
                "description": "Engaging blog content",
                "agents": ["researcher", "writer", "editor"],
                "steps": [
                    {
                        "name": "research",
                        "agent": "researcher",
                        "description": "Research topic and gather sources",
                        "min_sources": 5
                    },
                    {
                        "name": "draft",
                        "agent": "writer",
                        "description": "Write blog post draft",
                        "target_words": 1000
                    },
                    {
                        "name": "edit",
                        "agent": "editor",
                        "description": "Polish and finalize"
                    }
                ],
                "quality_checks": ["clarity", "engagement"]
            },
            "research_report": {
                "name": "Research Report",
                "description": "In-depth research with citations",
                "agents": ["researcher", "writer", "editor"],
                "steps": [
                    {
                        "name": "research",
                        "agent": "researcher",
                        "description": "Deep research and source gathering",
                        "min_sources": 15
                    },
                    {
                        "name": "draft",
                        "agent": "writer",
                        "description": "Write comprehensive report",
                        "target_words": 3000
                    },
                    {
                        "name": "edit",
                        "agent": "editor",
                        "description": "Final polish"
                    }
                ],
                "quality_checks": ["accuracy", "completeness", "citations"]
            }
        }
    
    def get_workflow(self, content_type: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow for content type.
        
        Args:
            content_type: Type of content
            
        Returns:
            Workflow definition or None if not found
        """
        workflow = self.workflows.get(content_type)
        
        if not workflow:
            logger.warning("workflow_not_found", content_type=content_type)
            return None
        
        logger.info("workflow_selected", content_type=content_type, workflow=workflow["name"])
        return workflow
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all available workflows.
        
        Returns:
            List of workflow information
        """
        return [
            {
                "content_type": content_type,
                "name": workflow["name"],
                "description": workflow["description"],
                "agents": workflow["agents"],
                "steps": len(workflow["steps"])
            }
            for content_type, workflow in self.workflows.items()
        ]
    
    def get_agent_for_step(
        self,
        content_type: str,
        step_name: str
    ) -> Optional[str]:
        """
        Get agent type for specific workflow step.
        
        Args:
            content_type: Type of content
            step_name: Name of workflow step
            
        Returns:
            Agent type or None if not found
        """
        workflow = self.get_workflow(content_type)
        
        if not workflow:
            return None
        
        for step in workflow["steps"]:
            if step["name"] == step_name:
                return step["agent"]
        
        return None
    
    def validate_workflow(self, content_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate workflow definition.
        
        Args:
            content_type: Type of content
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        workflow = self.workflows.get(content_type)
        
        if not workflow:
            return False, f"Workflow not found: {content_type}"
        
        # Check required fields
        required_fields = ["name", "description", "agents", "steps"]
        for field in required_fields:
            if field not in workflow:
                return False, f"Missing required field: {field}"
        
        # Check steps
        if not workflow["steps"]:
            return False, "Workflow must have at least one step"
        
        for step in workflow["steps"]:
            if "name" not in step:
                return False, "Step missing 'name' field"
            if "agent" not in step:
                return False, f"Step '{step.get('name')}' missing 'agent' field"
            if "description" not in step:
                return False, f"Step '{step.get('name')}' missing 'description' field"
        
        return True, None
    
    def get_quality_checks(self, content_type: str) -> List[str]:
        """
        Get quality checks for content type.
        
        Args:
            content_type: Type of content
            
        Returns:
            List of quality check names
        """
        workflow = self.get_workflow(content_type)
        
        if not workflow:
            return []
        
        return workflow.get("quality_checks", [])
