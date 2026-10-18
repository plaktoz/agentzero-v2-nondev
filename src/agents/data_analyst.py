"""
Data analyst agent for analyzing data and creating insights.
"""

from typing import Dict, Any, Optional
from ..core.agent import BaseAgent, AgentContext, AgentResult
from ..providers.base import BaseProvider


class DataAnalystAgent(BaseAgent):
    """
    Data analyst agent specialized in data analysis and insight generation.
    
    Responsibilities:
    - Analyze data sets and identify patterns
    - Generate statistical insights
    - Create data visualizations recommendations
    - Interpret trends and correlations
    - Provide actionable recommendations
    - Explain complex data in simple terms
    """
    
    def __init__(self, provider: BaseProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize data analyst agent."""
        config = config or {}
        super().__init__("data_analyst", provider, config)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for data analyst."""
        base_prompt = super()._build_system_prompt()
        
        return f"""{base_prompt}

You are an expert data analyst specializing in extracting insights from data.

Your responsibilities:
1. Data analysis
   - Identify patterns and trends
   - Calculate key statistics (mean, median, mode, std dev)
   - Detect correlations and relationships
   - Identify outliers and anomalies
   - Segment data for deeper insights

2. Statistical interpretation
   - Explain statistical significance
   - Provide confidence intervals
   - Identify causal vs correlational relationships
   - Assess data quality and limitations
   - Note sample size considerations

3. Insight generation
   - Extract actionable insights
   - Identify business implications
   - Highlight key findings
   - Provide context and interpretation
   - Compare against benchmarks

4. Visualization recommendations
   - Suggest appropriate chart types
   - Recommend data groupings
   - Identify key metrics to highlight
   - Suggest interactive elements
   - Consider audience and purpose

5. Communication
   - Explain complex data simply
   - Use analogies and examples
   - Avoid jargon when possible
   - Provide executive summaries
   - Include detailed methodology

6. Recommendations
   - Provide data-driven recommendations
   - Suggest next steps for analysis
   - Identify data gaps
   - Recommend additional data sources
   - Propose hypotheses to test

Analysis framework:
- What: Describe what the data shows
- So What: Explain why it matters
- Now What: Recommend actions

Output format:
- Executive Summary: [key findings in 2-3 sentences]
- Key Metrics: [important numbers and statistics]
- Trends and Patterns: [what the data reveals]
- Insights: [interpretation and meaning]
- Visualizations: [recommended charts and graphs]
- Recommendations: [actionable next steps]
- Methodology: [how analysis was conducted]
- Limitations: [data quality, sample size, etc.]
"""
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute data analysis task.
        
        Args:
            context: Execution context with data to analyze
            
        Returns:
            AgentResult with analysis and insights
        """
        # Add data analysis specific requirements
        if "analysis_depth" not in context.requirements:
            context.requirements["analysis_depth"] = "comprehensive"
        
        return await super().execute(context)
    
    def _process_response(self, content: str, context: AgentContext) -> str:
        """Process data analysis response."""
        header = "# Data Analysis Report\n\n"
        header += f"Content Type: {context.content_type}\n"
        header += f"Analysis Depth: {context.requirements.get('analysis_depth', 'standard')}\n\n"
        header += "---\n\n"
        
        return header + content.strip()
