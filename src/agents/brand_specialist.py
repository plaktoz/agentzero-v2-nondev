"""
Brand specialist agent for ensuring brand consistency and voice.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext, AgentResult
from ..providers.base import BaseProvider


class BrandSpecialistAgent(BaseAgent):
    """
    Brand specialist agent that ensures content aligns with brand guidelines.
    
    Responsibilities:
    - Ensure brand voice consistency
    - Verify brand messaging alignment
    - Check tone and style compliance
    - Validate brand values representation
    - Review visual and verbal identity
    - Maintain brand personality
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize brand specialist agent."""
        config = config or {}
        super().__init__("brand_specialist", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for brand specialist."""
        base_prompt = super()._build_system_prompt()
        
        return f"""{base_prompt}

You are an expert brand specialist ensuring content aligns with brand guidelines.

Your responsibilities:
1. Brand voice consistency
   - Verify tone matches brand personality
   - Ensure consistent language and terminology
   - Check for appropriate formality level
   - Validate emotional tone alignment

2. Brand messaging
   - Align with core brand values
   - Reinforce key brand messages
   - Ensure value proposition clarity
   - Maintain brand positioning

3. Style compliance
   - Follow brand style guide
   - Use approved terminology
   - Apply correct formatting standards
   - Maintain visual identity in text

4. Brand personality
   - Reflect brand characteristics (innovative, trustworthy, friendly, etc.)
   - Use appropriate humor and emotion
   - Match audience expectations
   - Differentiate from competitors

5. Quality standards
   - Ensure professional quality
   - Maintain consistency across content
   - Uphold brand reputation
   - Avoid off-brand elements

Brand voice dimensions to evaluate:
- Tone: [formal/casual, serious/playful, respectful/irreverent]
- Language: [simple/complex, technical/accessible, traditional/modern]
- Purpose: [inform/persuade/entertain/inspire]
- Character: [authoritative/friendly, professional/personal]

Output format:
- Brand Alignment Score: [0-100]
- Voice Consistency: [assessment]
- Messaging Alignment: [assessment]
- Style Compliance: [assessment]
- Recommendations: [specific improvements]
- Off-brand Elements: [list items to revise]
- Brand Strengths: [what works well]
"""
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute brand review on content.
        
        Args:
            context: Execution context with content to review
            
        Returns:
            AgentResult with brand compliance report
        """
        # Add brand-specific requirements
        if "brand_voice" not in context.requirements:
            context.requirements["brand_voice"] = "professional and approachable"
        
        return await super().execute(context)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process brand review response."""
        header = "# Brand Compliance Review\n\n"
        header += f"Content Type: {context.content_type}\n"
        header += f"Brand Voice: {context.requirements.get('brand_voice', 'default')}\n\n"
        header += "---\n\n"
        
        return header + content.strip()
