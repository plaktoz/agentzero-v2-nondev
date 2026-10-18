"""
Writer Agent - Creates content drafts based on research and requirements.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext
from ..providers.base import BaseProvider, Message


class WriterAgent(BaseAgent):
    """
    Specialized agent for content writing.
    Creates engaging, well-structured content based on research and requirements.
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """
        Initialize writer agent.
        
        Args:
            provider: LLM provider
            config: Agent configuration
        """
        super().__init__("writer", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for writer agent."""
        return """You are a content writer agent specialized in creating high-quality written content.

Your responsibilities:
1. Write clear, engaging, and well-structured content
2. Follow the content brief and requirements precisely
3. Incorporate research findings naturally
4. Maintain consistent voice and tone
5. Use proper formatting and structure

Writing Guidelines:
- Start with a compelling hook
- Use clear, concise language
- Include concrete examples and evidence
- Structure content logically with headings
- End with a strong conclusion or call-to-action
- Avoid jargon unless necessary (then explain it)
- Write for the target audience

Output Format:
Provide content in markdown format with:
- Clear title
- Proper heading hierarchy (H1, H2, H3)
- Well-organized paragraphs
- Bullet points or numbered lists where appropriate
- Emphasis (bold, italic) for key points"""
    
    def _build_user_message(self, context: AgentContext) -> str:
        """Build user message for writing task."""
        parts = [f"Writing Task: {context.requirements.get('step_description', 'Write content')}"]
        
        # Add topic/description
        if context.metadata.get("description"):
            parts.append(f"\nTopic: {context.metadata['description']}")
        
        # Add target word count
        target_words = context.requirements.get("target_words", 1000)
        parts.append(f"\nTarget Word Count: {target_words} words")
        
        # Add research notes if available
        if context.previous_output:
            parts.append(f"\nResearch Notes:\n{context.previous_output}")
        
        # Add specific requirements
        if context.requirements:
            parts.append("\nRequirements:")
            for key, value in context.requirements.items():
                if key not in ["step_description", "target_words"]:
                    parts.append(f"- {key}: {value}")
        
        parts.append("\nWrite engaging, well-structured content based on the research.")
        
        return "\n".join(parts)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process written content."""
        # Ensure proper markdown formatting
        content = content.strip()
        
        # Add title if missing
        if not content.startswith("#"):
            topic = context.metadata.get("description", "Content")
            content = f"# {topic}\n\n{content}"
        
        return content
