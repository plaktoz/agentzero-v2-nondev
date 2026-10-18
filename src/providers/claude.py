"""
Claude provider implementation using Anthropic API.
"""

import os
from typing import List, Optional, Dict, Any
import anthropic
from anthropic.types import Message as AnthropicMessage

from .base import BaseProvider, Message, ProviderResponse


class ClaudeProvider(BaseProvider):
    """Claude provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Claude provider.
        
        Args:
            config: Provider configuration
        """
        super().__init__(config)
        
        # Get API key from environment
        api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(f"API key not found in environment variable: {api_key_env}")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
    async def generate(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> ProviderResponse:
        """
        Generate response using Claude.
        
        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional parameters
            
        Returns:
            ProviderResponse with generated content
        """
        # Use provided values or fall back to config
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        # Convert messages to Anthropic format
        # Separate system message if present
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Call Claude API
        try:
            response: AnthropicMessage = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message if system_message else anthropic.NOT_GIVEN,
                messages=conversation_messages,
                **kwargs
            )
            
            # Extract content
            content = ""
            if response.content:
                # Handle both text and tool use blocks
                for block in response.content:
                    if hasattr(block, "text"):
                        content += block.text
            
            return ProviderResponse(
                content=content,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                model=response.model,
                finish_reason=response.stop_reason or "complete",
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason,
                }
            )
            
        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error: {str(e)}") from e
    
    def get_capabilities(self) -> List[str]:
        """Get Claude capabilities."""
        capabilities = [
            "long-context",  # 200K tokens
            "function-calling",
            "vision",
            "analysis",
            "writing",
        ]
        return capabilities
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Uses rough approximation: ~4 characters per token.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough approximation for Claude
        # More accurate would use tiktoken with cl100k_base
        return len(text) // 4
    
    def get_context_window(self) -> int:
        """Get context window size for Claude."""
        # Claude 3.5 Sonnet has 200K context window
        return 200_000
