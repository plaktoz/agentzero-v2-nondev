"""OpenAI GPT-4 provider implementation."""

import os
from typing import Dict, Any, Optional, List
import openai
from openai import AsyncOpenAI

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 provider implementation.
    
    Supports GPT-4, GPT-4 Turbo, and GPT-3.5 Turbo models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI provider.
        
        Args:
            config: Provider configuration including model, API key, etc.
        """
        super().__init__(config)
        
        # Get API key from environment
        api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(
                f"OpenAI API key not found. Set {api_key_env} environment variable."
            )
        
        # Initialize async client
        self.client = AsyncOpenAI(api_key=api_key)
        
        # Model configuration
        self.model = config.get("model", "gpt-4-turbo")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 1.0)
        self.frequency_penalty = config.get("frequency_penalty", 0.0)
        self.presence_penalty = config.get("presence_penalty", 0.0)
        
        # Rate limiting
        self.rate_limit_delay = config.get("rate_limit_delay", 0.0)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using OpenAI GPT models.
        
        Args:
            prompt: User prompt/message
            system_prompt: Optional system prompt for context
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Build messages
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Override defaults with kwargs
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            temperature = kwargs.get("temperature", self.temperature)
            top_p = kwargs.get("top_p", self.top_p)
            frequency_penalty = kwargs.get("frequency_penalty", self.frequency_penalty)
            presence_penalty = kwargs.get("presence_penalty", self.presence_penalty)
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            
            # Extract response text
            return response.choices[0].message.content
            
        except openai.RateLimitError as e:
            raise Exception(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text with conversation context.
        
        Args:
            prompt: Current user prompt
            context: List of previous messages [{"role": "user/assistant", "content": "..."}]
            system_prompt: Optional system prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            # Build messages with context
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add context messages
            messages.extend(context)
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Override defaults with kwargs
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            temperature = kwargs.get("temperature", self.temperature)
            top_p = kwargs.get("top_p", self.top_p)
            frequency_penalty = kwargs.get("frequency_penalty", self.frequency_penalty)
            presence_penalty = kwargs.get("presence_penalty", self.presence_penalty)
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            
            # Extract response text
            return response.choices[0].message.content
            
        except openai.RateLimitError as e:
            raise Exception(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"OpenAI generation with context failed: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        # Model context windows
        context_windows = {
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 16385,
            "gpt-3.5-turbo-16k": 16385
        }
        
        return {
            "provider": "openai",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "context_window": context_windows.get(self.model, 8192),
            "temperature": self.temperature,
            "supports_streaming": True,
            "supports_function_calling": True
        }
    
    async def count_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Note: This is an approximation. For exact counts, use tiktoken library.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Rough approximation: 1 token ≈ 4 characters
        # For production, use tiktoken library for accurate counts
        return len(text) // 4
    
    async def validate_config(self) -> bool:
        """Validate provider configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            Exception: If configuration is invalid
        """
        try:
            # Test API connection with minimal request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            raise Exception(f"OpenAI configuration validation failed: {str(e)}")
