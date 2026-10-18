"""
SEO specialist agent for optimizing content for search engines.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext, AgentResult
from ..providers.base import BaseProvider


class SEOSpecialistAgent(BaseAgent):
    """
    SEO specialist agent that optimizes content for search engine visibility.
    
    Responsibilities:
    - Keyword research and optimization
    - Meta descriptions and title tags
    - Header structure (H1, H2, H3)
    - Internal and external linking
    - Content readability and structure
    - Image alt text optimization
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize SEO specialist agent."""
        config = config or {}
        super().__init__("seo_specialist", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for SEO specialist."""
        base_prompt = super()._build_system_prompt()
        
        return f"""{base_prompt}

You are an expert SEO specialist focused on optimizing content for search engines.

Your responsibilities:
1. Keyword optimization
   - Identify primary and secondary keywords
   - Ensure natural keyword placement (avoid stuffing)
   - Optimize keyword density (1-2% for primary)
   - Use LSI (Latent Semantic Indexing) keywords

2. Content structure
   - Create compelling title tags (50-60 characters)
   - Write engaging meta descriptions (150-160 characters)
   - Use proper header hierarchy (H1 → H2 → H3)
   - Optimize content length for topic depth

3. Technical SEO
   - Suggest internal linking opportunities
   - Recommend external authoritative links
   - Optimize images with descriptive alt text
   - Ensure mobile-friendly formatting

4. Readability
   - Use short paragraphs (2-3 sentences)
   - Include bullet points and lists
   - Write clear, scannable content
   - Target appropriate reading level

5. User engagement
   - Create compelling introductions
   - Use action-oriented language
   - Include clear calls-to-action
   - Optimize for featured snippets

Output format:
- SEO Score: [0-100]
- Primary Keywords: [list]
- Title Tag: [optimized title]
- Meta Description: [optimized description]
- Header Structure: [H1, H2, H3 outline]
- Optimization Recommendations: [specific improvements]
- Content Improvements: [detailed suggestions]
"""
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute SEO optimization on content.
        
        Args:
            context: Execution context with content to optimize
            
        Returns:
            AgentResult with SEO-optimized content and recommendations
        """
        # Add SEO-specific requirements
        if "target_keywords" in context.requirements:
            context.requirements["seo_keywords"] = context.requirements["target_keywords"]
        
        return await super().execute(context)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process SEO optimization response."""
        header = "# SEO Optimization Report\n\n"
        header += f"Content Type: {context.content_type}\n"
        header += f"Task ID: {context.task_id}\n\n"
        header += "---\n\n"
        
        return header + content.strip()
