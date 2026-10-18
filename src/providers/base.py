"""
Base provider interface for LLM providers.
All provider implementations must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a message in the conversation."""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ProviderResponse:
    """Response from LLM provider."""
    content: str
    tokens_used: int
    model: str
    finish_reason: str
    metadata: Optional[Dict[str, Any]] = None


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration including model, api_key, etc.
        """
        self.config = config
        self.model = config.get("model")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)
        
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> ProviderResponse:
        """
        Generate response from the LLM.
        
        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate (overrides config)
            temperature: Temperature for generation (overrides config)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ProviderResponse with generated content and metadata
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of provider capabilities.
        
        Returns:
            List of capability strings (e.g., ["long-context", "function-calling"])
        """
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for given text.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        pass
    
    def supports_long_context(self) -> bool:
        """Check if provider supports long context (>100K tokens)."""
        return "long-context" in self.get_capabilities()
    
    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model
    
    def get_max_tokens(self) -> int:
        """Get maximum tokens configuration."""
        return self.max_tokens
