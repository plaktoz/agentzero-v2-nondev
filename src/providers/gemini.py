"""Google Gemini provider implementation."""

import os
from typing import Dict, Any, Optional, List
import google.generativeai as genai

from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation.
    
    Supports Gemini 1.5 Pro, Gemini 1.5 Flash, and Gemini Pro models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Gemini provider.
        
        Args:
            config: Provider configuration including model, API key, etc.
        """
        super().__init__(config)
        
        # Get API key from environment
        api_key_env = config.get("api_key_env", "GOOGLE_API_KEY")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(
                f"Google API key not found. Set {api_key_env} environment variable."
            )
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Model configuration
        self.model_name = config.get("model", "gemini-1.5-pro")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.95)
        self.top_k = config.get("top_k", 40)
        
        # Generation config
        self.generation_config = genai.GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k
        )
        
        # Safety settings (permissive for content creation)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
        
        # Rate limiting
        self.rate_limit_delay = config.get("rate_limit_delay", 0.0)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using Google Gemini models.
        
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
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Override generation config if kwargs provided
            if kwargs:
                generation_config = genai.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    top_p=kwargs.get("top_p", self.top_p),
                    top_k=kwargs.get("top_k", self.top_k)
                )
                
                # Create temporary model with custom config
                temp_model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings
                )
                response = await temp_model.generate_content_async(full_prompt)
            else:
                # Use default model
                response = await self.model.generate_content_async(full_prompt)
            
            # Extract response text
            if not response.parts:
                raise Exception("Empty response from Gemini")
            
            return response.text
            
        except Exception as e:
            # Handle safety blocks
            if hasattr(e, 'message') and 'SAFETY' in str(e):
                raise Exception(f"Gemini safety filter triggered: {str(e)}")
            raise Exception(f"Gemini generation failed: {str(e)}")
    
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
            # Start chat session
            chat = self.model.start_chat(history=[])
            
            # Add system prompt as first message if provided
            if system_prompt:
                await chat.send_message_async(
                    f"System instructions: {system_prompt}"
                )
            
            # Add context messages
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "user":
                    await chat.send_message_async(content)
                elif role == "assistant":
                    # For assistant messages, we need to add them to history
                    # Gemini doesn't have a direct way, so we simulate
                    pass
            
            # Override generation config if kwargs provided
            if kwargs:
                generation_config = genai.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    top_p=kwargs.get("top_p", self.top_p),
                    top_k=kwargs.get("top_k", self.top_k)
                )
                
                # Create new chat with custom config
                temp_model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings
                )
                chat = temp_model.start_chat(history=[])
            
            # Send current prompt
            response = await chat.send_message_async(prompt)
            
            # Extract response text
            if not response.parts:
                raise Exception("Empty response from Gemini")
            
            return response.text
            
        except Exception as e:
            if hasattr(e, 'message') and 'SAFETY' in str(e):
                raise Exception(f"Gemini safety filter triggered: {str(e)}")
            raise Exception(f"Gemini generation with context failed: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        # Model context windows
        context_windows = {
            "gemini-1.5-pro": 1048576,  # 1M tokens!
            "gemini-1.5-flash": 1048576,  # 1M tokens!
            "gemini-pro": 32768,
            "gemini-pro-vision": 16384
        }
        
        return {
            "provider": "gemini",
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "context_window": context_windows.get(self.model_name, 32768),
            "temperature": self.temperature,
            "supports_streaming": True,
            "supports_multimodal": "vision" in self.model_name or "1.5" in self.model_name
        }
    
    async def count_tokens(self, text: str) -> int:
        """Count tokens for text using Gemini's tokenizer.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Token count
        """
        try:
            # Use Gemini's built-in token counter
            result = await self.model.count_tokens_async(text)
            return result.total_tokens
        except Exception:
            # Fallback to approximation
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
            response = await self.model.generate_content_async("test")
            return True
        except Exception as e:
            raise Exception(f"Gemini configuration validation failed: {str(e)}")
