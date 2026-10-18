"""
Coordinator agent - Main orchestrator for all agent activities.
Handles request parsing, workflow selection, agent spawning, and result aggregation.
"""

import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import structlog

from .router import Router
from .agent import BaseAgent, AgentContext, AgentResult
from .communication import CommunicationMode, CommunicationProtocol
from ..providers.base import BaseProvider
from ..storage.documents import DocumentStorage, DocumentMetadata

logger = structlog.get_logger()


@dataclass
class ContentRequest:
    """Represents a content creation request."""
    request_id: str
    description: str
    content_type: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class WorkflowExecution:
    """Tracks workflow execution state."""
    request_id: str
    workflow_name: str
    steps: List[str]
    current_step: int
    results: Dict[str, AgentResult] = field(default_factory=dict)
    status: str = "running"  # running, completed, failed
    error: Optional[str] = None


class Coordinator:
    """
    Main coordinator for multi-agent content creation.
    Orchestrates workflows, spawns agents, and manages execution.
    """
    
    def __init__(
        self,
        provider: BaseProvider,
        storage: DocumentStorage,
        config: Dict[str, Any]
    ):
        """
        Initialize coordinator.
        
        Args:
            provider: LLM provider for agents
            storage: Document storage system
            config: System configuration
        """
        self.provider = provider
        self.storage = storage
        self.config = config
        self.router = Router(config)
        
        # Track active executions
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        logger.info("coordinator_initialized", provider=provider.get_model_name())
    
    async def request(
        self,
        description: str,
        content_type: Optional[str] = None,
        **requirements
    ) -> str:
        """
        Submit a content creation request.
        
        Args:
            description: Description of content to create
            content_type: Type of content (blog_post, research_report, etc.)
            **requirements: Additional requirements (word_count, sources, etc.)
            
        Returns:
            Request ID for tracking
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Auto-detect content type if not provided
        if not content_type:
            content_type = await self._detect_content_type(description)
        
        # Create request
        request = ContentRequest(
            request_id=request_id,
            description=description,
            content_type=content_type,
            requirements=requirements
        )
        
        logger.info(
            "request_received",
            request_id=request_id,
            content_type=content_type,
            description=description[:100]
        )
        
        # Start workflow execution
        await self._execute_workflow(request)
        
        return request_id
    
    async def _detect_content_type(self, description: str) -> str:
        """
        Auto-detect content type from description.
        
        Args:
            description: Content description
            
        Returns:
            Detected content type
        """
        description_lower = description.lower()
        
        # Simple keyword-based detection
        if any(word in description_lower for word in ["blog", "post", "article"]):
            return "blog_post"
        elif any(word in description_lower for word in ["research", "report", "study"]):
            return "research_report"
        elif any(word in description_lower for word in ["technical", "documentation", "docs"]):
            return "technical_docs"
        elif any(word in description_lower for word in ["marketing", "copy", "ad"]):
            return "marketing_copy"
        elif any(word in description_lower for word in ["social", "tweet", "post"]):
            return "social_media"
        else:
            # Default to blog post
            return "blog_post"
    
    async def _execute_workflow(self, request: ContentRequest) -> None:
        """
        Execute workflow for content request.
        
        Args:
            request: Content request
        """
        try:
            # Get workflow for content type
            workflow = self.router.get_workflow(request.content_type)
            
            if not workflow:
                raise ValueError(f"No workflow found for content type: {request.content_type}")
            
            # Create workflow execution tracker
            execution = WorkflowExecution(
                request_id=request.request_id,
                workflow_name=workflow["name"],
                steps=[step["name"] for step in workflow["steps"]],
                current_step=0
            )
            
            self.active_executions[request.request_id] = execution
            
            logger.info(
                "workflow_started",
                request_id=request.request_id,
                workflow=workflow["name"],
                steps=execution.steps
            )
            
            # Execute workflow steps
            context_data = {
                "description": request.description,
                "requirements": request.requirements
            }
            
            for step_idx, step in enumerate(workflow["steps"]):
                execution.current_step = step_idx
                
                logger.info(
                    "step_started",
                    request_id=request.request_id,
                    step=step["name"],
                    agent=step["agent"]
                )
                
                # Determine next agent type for communication mode
                next_agent_type = None
                if step_idx < len(workflow["steps"]) - 1:
                    next_agent_type = workflow["steps"][step_idx + 1]["agent"]
                
                # Create agent for this step with appropriate communication mode
                agent = await self._create_agent(step["agent"], next_agent_type)
                
                # Build context for agent
                context = AgentContext(
                    task_id=request.request_id,
                    content_type=request.content_type,
                    requirements={
                        **request.requirements,
                        "step_description": step["description"],
                        **step
                    },
                    previous_output=self._get_previous_output(execution),
                    metadata=context_data
                )
                
                # Execute agent
                result = await agent.execute(context)
                
                # Store result
                execution.results[step["name"]] = result
                
                if not result.success:
                    execution.status = "failed"
                    execution.error = result.error
                    logger.error(
                        "step_failed",
                        request_id=request.request_id,
                        step=step["name"],
                        error=result.error
                    )
                    return
                
                logger.info(
                    "step_completed",
                    request_id=request.request_id,
                    step=step["name"],
                    tokens_used=result.tokens_used
                )
                
                # Update context for next step
                context_data[step["name"]] = result.content
            
            # Workflow completed successfully
            execution.status = "completed"
            
            # Save final document
            await self._save_document(request, execution)
            
            logger.info(
                "workflow_completed",
                request_id=request.request_id,
                total_tokens=sum(r.tokens_used for r in execution.results.values())
            )
            
        except Exception as e:
            logger.error(
                "workflow_failed",
                request_id=request.request_id,
                error=str(e)
            )
            if request.request_id in self.active_executions:
                self.active_executions[request.request_id].status = "failed"
                self.active_executions[request.request_id].error = str(e)
    
    async def _create_agent(self, agent_type: str, next_agent_type: Optional[str] = None) -> BaseAgent:
        """
        Create agent instance with appropriate communication mode.
        
        Args:
            agent_type: Type of agent to create
            next_agent_type: Optional next agent in workflow (for communication mode)
            
        Returns:
            Agent instance with appropriate communication mode
        """
        # Import agent classes dynamically to avoid circular imports
        from ..agents.researcher import ResearcherAgent
        from ..agents.writer import WriterAgent
        from ..agents.editor import EditorAgent
        from ..agents.fact_checker import FactCheckerAgent
        from ..agents.seo_specialist import SEOSpecialistAgent
        from ..agents.technical_writer import TechnicalWriterAgent
        from ..agents.copywriter import CopywriterAgent
        from ..agents.brand_specialist import BrandSpecialistAgent
        from ..agents.data_analyst import DataAnalystAgent
        
        # Determine communication mode based on next agent
        if next_agent_type:
            comm_mode = CommunicationProtocol.get_communication_mode(
                agent_type, next_agent_type
            )
        else:
            # Last agent in workflow - output for humans
            comm_mode = CommunicationMode.UNSLOP
        
        agent_classes = {
            "researcher": ResearcherAgent,
            "writer": WriterAgent,
            "editor": EditorAgent,
            "fact_checker": FactCheckerAgent,
            "seo_specialist": SEOSpecialistAgent,
            "technical_writer": TechnicalWriterAgent,
            "copywriter": CopywriterAgent,
            "brand_specialist": BrandSpecialistAgent,
            "data_analyst": DataAnalystAgent,
        }
        
        agent_class = agent_classes.get(agent_type)
        if not agent_class:
            # Fall back to base agent
            return BaseAgent(agent_type, self.provider, communication_mode=comm_mode)
        
        # Create agent and set communication mode
        agent = agent_class(self.provider, self.config.get("agents", {}).get(agent_type, {}))
        agent.set_communication_mode(comm_mode)
        
        return agent
    
    def _get_previous_output(self, execution: WorkflowExecution) -> Optional[str]:
        """
        Get output from previous workflow step.
        
        Args:
            execution: Workflow execution
            
        Returns:
            Previous step output or None
        """
        if execution.current_step == 0:
            return None
        
        previous_step = execution.steps[execution.current_step - 1]
        result = execution.results.get(previous_step)
        
        return result.content if result else None
    
    async def _save_document(
        self,
        request: ContentRequest,
        execution: WorkflowExecution
    ) -> None:
        """
        Save final document to storage.
        
        Args:
            request: Original request
            execution: Completed workflow execution
        """
        # Get final content (from last step)
        final_step = execution.steps[-1]
        final_result = execution.results[final_step]
        
        # Create metadata
        metadata = DocumentMetadata(
            id=request.request_id,
            title=request.description[:100],
            content_type=request.content_type,
            status="draft",
            created_at=request.created_at,
            updated_at=datetime.utcnow().isoformat(),
            author="system",
            version=1,
            word_count=len(final_result.content.split()),
            tags=[request.content_type]
        )
        
        # Save document
        await self.storage.save_document(
            doc_id=request.request_id,
            content=final_result.content,
            metadata=metadata,
            status="draft"
        )
        
        logger.info(
            "document_saved",
            request_id=request.request_id,
            word_count=metadata.word_count
        )
    
    async def get_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get status of content request.
        
        Args:
            request_id: Request ID
            
        Returns:
            Status information
        """
        execution = self.active_executions.get(request_id)
        
        if not execution:
            return {
                "request_id": request_id,
                "status": "not_found"
            }
        
        return {
            "request_id": request_id,
            "workflow": execution.workflow_name,
            "status": execution.status,
            "current_step": execution.current_step,
            "total_steps": len(execution.steps),
            "steps": execution.steps,
            "completed_steps": list(execution.results.keys()),
            "error": execution.error,
            "total_tokens": sum(r.tokens_used for r in execution.results.values())
        }
    
    async def list_requests(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all content requests.
        
        Args:
            status: Filter by status (running, completed, failed)
            
        Returns:
            List of request information
        """
        requests = []
        
        for request_id, execution in self.active_executions.items():
            if status and execution.status != status:
                continue
            
            requests.append({
                "request_id": request_id,
                "workflow": execution.workflow_name,
                "status": execution.status,
                "current_step": execution.current_step,
                "total_steps": len(execution.steps),
            })
        
        return requests
