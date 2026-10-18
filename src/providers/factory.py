"""Provider factory for creating LLM provider instances."""

from typing import Dict, Any
from .base import LLMProvider
from .claude import ClaudeProvider
from .openai import OpenAIProvider
from .gemini import GeminiProvider


class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    # Registry of available providers
    PROVIDERS = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider
    }
    
    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        config: Dict[str, Any]
    ) -> LLMProvider:
        """Create a provider instance.
        
        Args:
            provider_name: Name of the provider (claude, openai, gemini)
            config: Provider configuration
            
        Returns:
            Initialized provider instance
            
        Raises:
            ValueError: If provider name is not supported
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls.PROVIDERS:
            available = ", ".join(cls.PROVIDERS.keys())
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {available}"
            )
        
        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(config)
    
    @classmethod
    def create_from_config(
        cls,
        full_config: Dict[str, Any],
        provider_name: str = None
    ) -> LLMProvider:
        """Create provider from full system configuration.
        
        Args:
            full_config: Full system configuration with providers section
            provider_name: Optional provider name to use. If not provided,
                          uses default_provider from system config
            
        Returns:
            Initialized provider instance
            
        Raises:
            ValueError: If provider is not configured or not enabled
        """
        # Get provider name
        if provider_name is None:
            provider_name = full_config.get("system", {}).get(
                "default_provider", "claude"
            )
        
        provider_name = provider_name.lower()
        
        # Get provider config
        providers_config = full_config.get("providers", {})
        provider_config = providers_config.get(provider_name)
        
        if not provider_config:
            raise ValueError(
                f"Provider '{provider_name}' not found in configuration"
            )
        
        # Check if provider is enabled
        if not provider_config.get("enabled", False):
            raise ValueError(
                f"Provider '{provider_name}' is not enabled in configuration"
            )
        
        # Create provider
        return cls.create_provider(provider_name, provider_config)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names.
        
        Returns:
            List of provider names
        """
        return list(cls.PROVIDERS.keys())
    
    @classmethod
    def is_provider_available(cls, provider_name: str) -> bool:
        """Check if a provider is available.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            True if provider is available
        """
        return provider_name.lower() in cls.PROVIDERS
    
    @classmethod
    def register_provider(
        cls,
        name: str,
        provider_class: type
    ) -> None:
        """Register a custom provider.
        
        Args:
            name: Provider name
            provider_class: Provider class (must inherit from LLMProvider)
            
        Raises:
            TypeError: If provider_class doesn't inherit from LLMProvider
        """
        if not issubclass(provider_class, LLMProvider):
            raise TypeError(
                f"Provider class must inherit from LLMProvider, "
                f"got {provider_class}"
            )
        
        cls.PROVIDERS[name.lower()] = provider_class


def create_provider(
    provider_name: str,
    config: Dict[str, Any]
) -> LLMProvider:
    """Convenience function to create a provider.
    
    Args:
        provider_name: Name of the provider
        config: Provider configuration
        
    Returns:
        Initialized provider instance
    """
    return ProviderFactory.create_provider(provider_name, config)


def create_provider_from_config(
    full_config: Dict[str, Any],
    provider_name: str = None
) -> LLMProvider:
    """Convenience function to create provider from full config.
    
    Args:
        full_config: Full system configuration
        provider_name: Optional provider name
        
    Returns:
        Initialized provider instance
    """
    return ProviderFactory.create_from_config(full_config, provider_name)
