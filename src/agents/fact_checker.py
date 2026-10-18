"""
Fact-checker agent for verifying factual claims and data accuracy.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext, AgentResult
from ..providers.base import BaseProvider


class FactCheckerAgent(BaseAgent):
    """
    Fact-checker agent that verifies factual claims, statistics, and citations.
    
    Responsibilities:
    - Verify factual claims against reliable sources
    - Check data and statistics for accuracy
    - Validate citations and references
    - Flag unverifiable or questionable claims
    - Provide confidence scores for claims
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize fact-checker agent."""
        config = config or {}
        super().__init__("fact_checker", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for fact-checker."""
        base_prompt = super()._build_system_prompt()
        
        return f"""{base_prompt}

You are a meticulous fact-checker responsible for verifying the accuracy of content.

Your responsibilities:
1. Identify all factual claims, statistics, and data points
2. Verify each claim against reliable sources
3. Check citations and references for accuracy
4. Flag any unverifiable or questionable claims
5. Provide confidence scores (high/medium/low) for each claim
6. Suggest corrections for inaccurate information

Verification criteria:
- Use authoritative sources (academic papers, official statistics, reputable news)
- Cross-reference multiple sources when possible
- Note the recency of information (is it current?)
- Identify potential biases or conflicts of interest
- Distinguish between facts, opinions, and speculation

Output format:
For each claim:
- Claim: [the factual statement]
- Status: [verified/unverified/false/needs-update]
- Confidence: [high/medium/low]
- Sources: [list of sources that support or refute]
- Notes: [any additional context or concerns]

Final summary:
- Overall accuracy score (0-100)
- Number of verified/unverified/false claims
- Critical issues that must be addressed
- Recommendations for improvement
"""
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute fact-checking on content.
        
        Args:
            context: Execution context with content to verify
            
        Returns:
            AgentResult with fact-check report
        """
        # Add fact-checking specific instructions to context
        if "requirements" not in context.requirements:
            context.requirements["fact_check_instructions"] = (
                "Thoroughly verify all factual claims, statistics, and citations. "
                "Provide detailed verification report with confidence scores."
            )
        
        return await super().execute(context)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process fact-check response."""
        # Add fact-check metadata header
        header = "# Fact-Check Report\n\n"
        header += f"Content Type: {context.content_type}\n"
        header += f"Task ID: {context.task_id}\n\n"
        header += "---\n\n"
        
        return header + content.strip()
