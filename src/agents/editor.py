"""
Editor Agent - Polishes and finalizes content.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext
from ..providers.base import BaseProvider, Message


class EditorAgent(BaseAgent):
    """
    Specialized agent for editing and polishing content.
    Improves clarity, consistency, and overall quality.
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """
        Initialize editor agent.
        
        Args:
            provider: LLM provider
            config: Agent configuration
        """
        super().__init__("editor", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for editor agent."""
        return """You are an editor agent specialized in polishing and improving written content.

Your responsibilities:
1. Improve clarity and readability
2. Ensure consistent voice and tone
3. Fix grammar, spelling, and punctuation
4. Enhance flow and transitions
5. Strengthen weak sections
6. Remove redundancy and wordiness
7. Verify formatting and structure

Editing Guidelines:
- Preserve the author's voice and intent
- Make content more engaging and readable
- Ensure logical flow between sections
- Check for consistency in terminology
- Improve sentence variety and rhythm
- Strengthen opening and closing
- Verify all formatting is correct

Quality Checks:
- Clarity: Is the message clear?
- Engagement: Is it compelling?
- Consistency: Is voice/tone consistent?
- Completeness: Are all points covered?
- Correctness: Grammar, spelling, facts

Output Format:
Provide the edited content in markdown format, maintaining the original structure but with improvements throughout."""
    
    def _build_user_message(self, context: AgentContext) -> str:
        """Build user message for editing task."""
        parts = [f"Editing Task: {context.requirements.get('step_description', 'Edit and polish content')}"]
        
        # Add content to edit
        if context.previous_output:
            parts.append(f"\nContent to Edit:\n{context.previous_output}")
        else:
            parts.append("\nError: No content provided for editing")
        
        # Add specific requirements
        if context.requirements:
            parts.append("\nFocus Areas:")
            for key, value in context.requirements.items():
                if key not in ["step_description"]:
                    parts.append(f"- {key}: {value}")
        
        parts.append("\nProvide the edited and polished version of the content.")
        
        return "\n".join(parts)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process edited content."""
        return content.strip()
