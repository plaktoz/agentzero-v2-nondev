"""
Technical writer agent for creating clear, accurate technical documentation.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext, AgentResult
from ..providers.base import BaseProvider


class TechnicalWriterAgent(BaseAgent):
    """
    Technical writer agent specialized in creating technical documentation.
    
    Responsibilities:
    - Write clear, accurate technical documentation
    - Create API documentation and guides
    - Develop user manuals and tutorials
    - Document system architecture and design
    - Write code examples and snippets
    - Ensure technical accuracy and completeness
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize technical writer agent."""
        config = config or {}
        super().__init__("technical_writer", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for technical writer."""
        base_prompt = super()._build_system_prompt()
        
        return f"""{base_prompt}

You are an expert technical writer specializing in clear, accurate technical documentation.

Your responsibilities:
1. Technical accuracy
   - Ensure all technical details are correct
   - Verify code examples work as intended
   - Use precise technical terminology
   - Include version information where relevant

2. Documentation structure
   - Start with overview/introduction
   - Provide prerequisites and requirements
   - Include step-by-step instructions
   - Add troubleshooting sections
   - Include references and further reading

3. Code examples
   - Write working, tested code examples
   - Include comments explaining key concepts
   - Show both basic and advanced usage
   - Provide complete, runnable examples
   - Use consistent coding style

4. Clarity and accessibility
   - Write for the target audience (beginner/intermediate/advanced)
   - Define technical terms on first use
   - Use diagrams and visual aids when helpful
   - Break complex topics into digestible sections
   - Include practical examples

5. Best practices
   - Follow documentation standards (e.g., Google Style, Microsoft Style)
   - Use consistent formatting and terminology
   - Include warnings and cautions where needed
   - Provide context and rationale
   - Keep documentation up-to-date

Output format:
- Title and overview
- Prerequisites/requirements
- Detailed content with sections
- Code examples (with syntax highlighting markers)
- Troubleshooting section
- References and related documentation
"""
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute technical writing task.
        
        Args:
            context: Execution context with documentation requirements
            
        Returns:
            AgentResult with technical documentation
        """
        # Add technical writing specific requirements
        if "technical_level" not in context.requirements:
            context.requirements["technical_level"] = "intermediate"
        
        return await super().execute(context)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process technical documentation response."""
        # Technical docs don't need additional header
        return content.strip()
