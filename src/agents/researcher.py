"""
Researcher Agent - Gathers sources and conducts research.
"""

from typing import Dict, Any, List, Optional
from ..core.agent import BaseAgent, AgentContext
from ..providers.base import BaseProvider, Message


class ResearcherAgent(BaseAgent):
    """
    Specialized agent for research and source gathering.
    Focuses on finding credible sources and synthesizing information.
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """
        Initialize researcher agent.
        
        Args:
            provider: LLM provider
            config: Agent configuration
        """
        super().__init__("researcher", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for researcher agent."""
        return """You are a research agent specialized in gathering information and sources.

Your responsibilities:
1. Find credible, authoritative sources on the given topic
2. Synthesize information from multiple sources
3. Identify key facts, trends, and insights
4. Provide proper citations and references
5. Note any conflicting information or gaps in research

Research Guidelines:
- Prioritize recent, authoritative sources
- Include diverse perspectives
- Verify facts across multiple sources
- Note confidence level for claims
- Organize findings logically

Output Format:
Provide research notes in markdown format with:
- Executive summary of findings
- Key insights (bullet points)
- Detailed notes organized by subtopic
- Source list with citations
- Gaps or areas needing more research"""
    
    def _build_user_message(self, context: AgentContext) -> str:
        """Build user message for research task."""
        parts = [f"Research Task: {context.requirements.get('step_description', 'Research topic')}"]
        
        # Add topic/description
        if context.metadata.get("description"):
            parts.append(f"\nTopic: {context.metadata['description']}")
        
        # Add minimum sources requirement
        min_sources = context.requirements.get("min_sources", 5)
        parts.append(f"\nMinimum Sources Required: {min_sources}")
        
        # Add specific requirements
        if context.requirements:
            parts.append("\nRequirements:")
            for key, value in context.requirements.items():
                if key not in ["step_description", "min_sources"]:
                    parts.append(f"- {key}: {value}")
        
        parts.append("\nProvide comprehensive research notes with sources.")
        
        return "\n".join(parts)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process research output."""
        # Ensure proper markdown formatting
        if not content.startswith("#"):
            content = f"# Research Notes\n\n{content}"
        
        return content.strip()