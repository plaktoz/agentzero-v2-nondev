"""
Communication modes for agent interactions.

Implements efficient agent-to-agent communication (caveman mode) 
and clear human-facing communication (unslop mode).
"""

from enum import Enum
from typing import Dict, Any, Optional


class CommunicationMode(Enum):
    """Communication modes for different audiences."""
    
    CAVEMAN = "caveman"  # Efficient, abbreviated for agent-to-agent
    UNSLOP = "unslop"    # Clear, complete for human-facing


class MessageFormatter:
    """Formats messages based on communication mode."""
    
    @staticmethod
    def format_context(
        context: Dict[str, Any],
        mode: CommunicationMode = CommunicationMode.UNSLOP
    ) -> str:
        """Format context information based on communication mode.
        
        Args:
            context: Context dictionary with task information
            mode: Communication mode to use
            
        Returns:
            Formatted context string
        """
        if mode == CommunicationMode.CAVEMAN:
            return MessageFormatter._format_caveman(context)
        else:
            return MessageFormatter._format_unslop(context)
    
    @staticmethod
    def _format_caveman(context: Dict[str, Any]) -> str:
        """Format in caveman mode - abbreviated, efficient.
        
        Uses:
        - Abbreviations (req, prev, res)
        - Symbols (→, •, #)
        - Minimal punctuation
        - Short phrases
        """
        parts = []
        
        # Task ID
        if "task_id" in context:
            parts.append(f"#task:{context['task_id'][:8]}")
        
        # Content type
        if "content_type" in context:
            parts.append(f"type:{context['content_type']}")
        
        # Requirements - abbreviated
        if "requirements" in context and context["requirements"]:
            parts.append("req:")
            for key, value in context["requirements"].items():
                # Abbreviate common keys
                abbrev_key = MessageFormatter._abbreviate_key(key)
                parts.append(f"• {abbrev_key}:{value}")
        
        # Research notes - condensed
        if "research_notes" in context and context["research_notes"]:
            notes = context["research_notes"]
            # Truncate if too long
            if len(notes) > 500:
                notes = notes[:500] + "..."
            parts.append(f"res→{notes}")
        
        # Previous output - reference only
        if "previous_output" in context and context["previous_output"]:
            prev = context["previous_output"]
            # Just show length and first line
            first_line = prev.split('\n')[0][:50]
            parts.append(f"prev({len(prev)}ch)→{first_line}...")
        
        return "\n".join(parts)
    
    @staticmethod
    def _format_unslop(context: Dict[str, Any]) -> str:
        """Format in unslop mode - clear, complete, educational.
        
        Uses:
        - Full words and sentences
        - Proper grammar and structure
        - Concrete examples
        - Educational explanations
        """
        parts = []
        
        # Task ID with explanation
        if "task_id" in context:
            parts.append(f"Task ID: {context['task_id']}")
            parts.append("This is your unique task identifier for tracking and reference.")
        
        # Content type with description
        if "content_type" in context:
            content_type = context['content_type']
            parts.append(f"\nContent Type: {content_type}")
            parts.append(f"You are creating {content_type} content.")
        
        # Requirements - detailed
        if "requirements" in context and context["requirements"]:
            parts.append("\nRequirements:")
            parts.append("Please ensure your output meets these specifications:")
            for key, value in context["requirements"].items():
                parts.append(f"  • {key.replace('_', ' ').title()}: {value}")
        
        # Research notes - full content
        if "research_notes" in context and context["research_notes"]:
            parts.append("\nResearch Notes:")
            parts.append("The following research has been gathered for this task:")
            parts.append(context["research_notes"])
        
        # Previous output - full content
        if "previous_output" in context and context["previous_output"]:
            parts.append("\nPrevious Output:")
            parts.append("Here is the previous work that you should build upon or refine:")
            parts.append(context["previous_output"])
        
        return "\n".join(parts)
    
    @staticmethod
    def _abbreviate_key(key: str) -> str:
        """Abbreviate common context keys for caveman mode."""
        abbreviations = {
            "target_words": "words",
            "word_count": "words",
            "min_sources": "src",
            "max_sources": "src_max",
            "target_keywords": "kw",
            "seo_optimize": "seo",
            "tone": "tone",
            "audience": "aud",
            "format": "fmt",
            "deadline": "due",
            "priority": "pri",
            "research_depth": "depth",
        }
        return abbreviations.get(key, key[:4])
    
    @staticmethod
    def format_handoff(
        from_agent: str,
        to_agent: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        mode: CommunicationMode = CommunicationMode.CAVEMAN
    ) -> str:
        """Format agent-to-agent handoff message.
        
        Args:
            from_agent: Source agent type
            to_agent: Destination agent type
            content: Content to hand off
            metadata: Optional metadata
            mode: Communication mode
            
        Returns:
            Formatted handoff message
        """
        if mode == CommunicationMode.CAVEMAN:
            parts = [f"{from_agent}→{to_agent}"]
            
            if metadata:
                # Add key metadata only
                if "tokens" in metadata:
                    parts.append(f"tok:{metadata['tokens']}")
                if "quality_score" in metadata:
                    parts.append(f"q:{metadata['quality_score']}")
            
            parts.append(f"out→{content}")
            return "\n".join(parts)
        
        else:  # UNSLOP mode
            parts = [
                f"Handoff from {from_agent.title()} to {to_agent.title()}",
                "",
                "The previous agent has completed their work. Here is what they produced:",
                ""
            ]
            
            if metadata:
                parts.append("Metadata:")
                for key, value in metadata.items():
                    parts.append(f"  • {key.replace('_', ' ').title()}: {value}")
                parts.append("")
            
            parts.append("Content:")
            parts.append(content)
            
            return "\n".join(parts)
    
    @staticmethod
    def format_system_prompt(
        agent_type: str,
        mode: CommunicationMode = CommunicationMode.UNSLOP
    ) -> str:
        """Format system prompt based on communication mode.
        
        Args:
            agent_type: Type of agent
            mode: Communication mode
            
        Returns:
            Formatted system prompt
        """
        if mode == CommunicationMode.CAVEMAN:
            # Efficient system prompt for agent-to-agent
            return (
                f"You are {agent_type} agent. "
                f"Input=abbreviated. Output=efficient. "
                f"Use symbols, abbrev, short phrases. "
                f"Focus on content quality."
            )
        else:
            # Clear system prompt for human-facing
            return (
                f"You are a professional {agent_type} agent. "
                f"Your role is to produce high-quality {agent_type} work. "
                f"Write clearly and completely. Use proper grammar and structure. "
                f"Provide concrete examples and educational explanations. "
                f"Your output will be read by humans, so make it clear and engaging."
            )


class CommunicationProtocol:
    """Protocol for agent communication."""
    
    @staticmethod
    def should_use_caveman_mode(
        source: str,
        destination: str
    ) -> bool:
        """Determine if caveman mode should be used.
        
        Args:
            source: Source of communication (agent type or "human")
            destination: Destination (agent type or "human")
            
        Returns:
            True if caveman mode should be used
        """
        # Use caveman mode only for agent-to-agent communication
        agent_types = {
            "researcher", "writer", "editor", "fact_checker",
            "seo_specialist", "technical_writer", "copywriter",
            "brand_specialist", "data_analyst", "coordinator"
        }
        
        return (
            source in agent_types and 
            destination in agent_types and
            source != "coordinator"  # Coordinator uses unslop mode
        )
    
    @staticmethod
    def get_communication_mode(
        source: str,
        destination: str
    ) -> CommunicationMode:
        """Get appropriate communication mode.
        
        Args:
            source: Source of communication
            destination: Destination
            
        Returns:
            Communication mode to use
        """
        if CommunicationProtocol.should_use_caveman_mode(source, destination):
            return CommunicationMode.CAVEMAN
        else:
            return CommunicationMode.UNSLOP
