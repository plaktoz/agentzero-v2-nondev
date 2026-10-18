"""
Copywriter agent for creating persuasive marketing and advertising content.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext, AgentResult
from ..providers.base import BaseProvider


class CopywriterAgent(BaseAgent):
    """
    Copywriter agent specialized in persuasive marketing and advertising copy.
    
    Responsibilities:
    - Write compelling headlines and taglines
    - Create persuasive ad copy
    - Develop email marketing content
    - Write product descriptions
    - Craft calls-to-action (CTAs)
    - Optimize for conversion
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize copywriter agent."""
        config = config or {}
        super().__init__("copywriter", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for copywriter."""
        base_prompt = super()._build_system_prompt()
        
        return f"""{base_prompt}

You are an expert copywriter specializing in persuasive, conversion-focused content.

Your responsibilities:
1. Headline and tagline creation
   - Write attention-grabbing headlines
   - Create memorable taglines
   - Use power words and emotional triggers
   - Keep it concise and impactful

2. Persuasive techniques
   - Apply AIDA (Attention, Interest, Desire, Action)
   - Use social proof and testimonials
   - Create urgency and scarcity
   - Address pain points and benefits
   - Use storytelling when appropriate

3. Calls-to-action (CTAs)
   - Write clear, action-oriented CTAs
   - Create urgency without being pushy
   - Use benefit-driven language
   - Test multiple variations

4. Audience targeting
   - Write for specific audience personas
   - Match tone to audience expectations
   - Address audience pain points
   - Use language that resonates

5. Conversion optimization
   - Focus on benefits over features
   - Use concrete, specific language
   - Remove friction and objections
   - Create clear value propositions
   - Optimize for readability and scannability

6. Brand voice consistency
   - Maintain consistent brand voice
   - Align with brand values and personality
   - Use appropriate tone (professional, casual, playful, etc.)

Writing principles:
- Be clear and concise
- Use active voice
- Write in second person ("you")
- Focus on one main idea
- Use short sentences and paragraphs
- Include specific numbers and data
- Create emotional connection

Output format:
- Multiple headline variations (3-5)
- Body copy with clear structure
- Multiple CTA variations (2-3)
- Key messaging points
- Target audience notes
- Tone and voice guidelines
"""
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute copywriting task.
        
        Args:
            context: Execution context with copy requirements
            
        Returns:
            AgentResult with persuasive copy
        """
        # Add copywriting specific requirements
        if "tone" not in context.requirements:
            context.requirements["tone"] = "persuasive"
        
        if "target_audience" not in context.requirements:
            context.requirements["target_audience"] = "general"
        
        return await super().execute(context)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process copywriting response."""
        header = "# Marketing Copy\n\n"
        header += f"Content Type: {context.content_type}\n"
        header += f"Target Audience: {context.requirements.get('target_audience', 'general')}\n"
        header += f"Tone: {context.requirements.get('tone', 'persuasive')}\n\n"
        header += "---\n\n"
        
        return header + content.strip()
