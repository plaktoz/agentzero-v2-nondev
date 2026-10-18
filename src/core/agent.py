"""
Base agent class for all agent types.
"""

import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from ..providers.base import BaseProvider, Message, ProviderResponse
from .communication import (
    CommunicationMode,
    MessageFormatter,
    CommunicationProtocol
)


@dataclass
class AgentContext:
    """Context information for agent execution."""
    task_id: str
    content_type: str
    requirements: Dict[str, Any]
    research_notes: Optional[str] = None
    previous_output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from agent execution."""
    agent_id: str
    agent_type: str
    content: str
    tokens_used: int
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(
        self,
        agent_type: str,
        provider: BaseProvider,
        config: Optional[Dict[str, Any]] = None,
        communication_mode: Optional[CommunicationMode] = None
    ):
        """
        Initialize agent.
        
        Args:
            agent_type: Type of agent (e.g., "researcher", "writer")
            provider: LLM provider to use
            config: Agent-specific configuration
            communication_mode: Communication mode (caveman for agent-to-agent, unslop for human-facing)
        """
        self.agent_id = str(uuid.uuid4())
        self.agent_type = agent_type
        self.provider = provider
        self.config = config or {}
        self.communication_mode = communication_mode or CommunicationMode.UNSLOP
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """
        Build system prompt for this agent type.
        Uses communication mode to format appropriately.
        Override in subclasses for specialized behavior.
        
        Returns:
            System prompt string
        """
        return MessageFormatter.format_system_prompt(
            self.agent_type,
            self.communication_mode
        )
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute agent task.
        
        Args:
            context: Execution context with task details
            
        Returns:
            AgentResult with output and metadata
        """
        try:
            # Build messages
            messages = self._build_messages(context)
            
            # Generate response
            response: ProviderResponse = await self.provider.generate(
                messages=messages,
                max_tokens=self.config.get("max_tokens"),
                temperature=self.config.get("temperature"),
            )
            
            # Process response
            processed_content = self._process_response(response.content, context)
            
            return AgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content=processed_content,
                tokens_used=response.tokens_used,
                success=True,
                metadata={
                    "model": response.model,
                    "finish_reason": response.finish_reason,
                    "provider_metadata": response.metadata,
                }
            )
            
        except Exception as e:
            return AgentResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                content="",
                tokens_used=0,
                success=False,
                error=str(e),
            )
    
    def _build_messages(self, context: AgentContext) -> List[Message]:
        """
        Build message list for LLM.
        Override in subclasses for specialized message construction.
        
        Args:
            context: Execution context
            
        Returns:
            List of messages
        """
        messages = [
            Message(role="system", content=self.system_prompt)
        ]
        
        # Add context information
        user_message = self._build_user_message(context)
        messages.append(Message(role="user", content=user_message))
        
        return messages
    
    def _build_user_message(self, context: AgentContext) -> str:
        """
        Build user message from context using appropriate communication mode.
        Uses caveman mode for agent-to-agent, unslop mode for human-facing.
        Override in subclasses for specialized formatting.
        
        Args:
            context: Execution context
            
        Returns:
            User message string formatted according to communication mode
        """
        # Convert context to dictionary for formatter
        context_dict = {
            "task_id": context.task_id,
            "content_type": context.content_type,
            "requirements": context.requirements,
            "research_notes": context.research_notes,
            "previous_output": context.previous_output,
        }
        
        # Format using communication mode
        return MessageFormatter.format_context(
            context_dict,
            self.communication_mode
        )
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """
        Process LLM response.
        Override in subclasses for specialized post-processing.
        
        Args:
            content: Raw LLM response
            context: Execution context
            
        Returns:
            Processed content

    
    def handoff_to(
        self,
        target_agent_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format content for handoff to another agent.
        Uses appropriate communication mode based on agent types.
        
        Args:
            target_agent_type: Type of agent receiving the handoff
            content: Content to hand off
            metadata: Optional metadata about the work
            
        Returns:
            Formatted handoff message
        """
        # Determine communication mode for this handoff
        mode = CommunicationProtocol.get_communication_mode(
            self.agent_type,
            target_agent_type
        )
        
        return MessageFormatter.format_handoff(
            from_agent=self.agent_type,
            to_agent=target_agent_type,
            content=content,
            metadata=metadata,
            mode=mode
        )
    
    def set_communication_mode(self, mode: CommunicationMode) -> None:
        """
        Set communication mode for this agent.
        
        Args:
            mode: Communication mode to use
        """
        self.communication_mode = mode
        # Rebuild system prompt with new mode
        self.system_prompt = self._build_system_prompt()

        """
        return content.strip()
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "provider": self.provider.get_model_name(),
            "config": self.config,
        }
