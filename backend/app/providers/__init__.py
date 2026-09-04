from .base import BaseLLMProvider
from .ollama_provider import OllamaProvider
from .cloud_provider import ClaudeProvider, OpenAIProvider

def get_llm_provider(provider_name: str = "ollama", model_name: str = None) -> BaseLLMProvider:
    """Factory function to dynamically instantiate requested LLM provider."""
    provider_name = (provider_name or "ollama").lower()
    
    if provider_name == "claude" or provider_name == "anthropic":
        return ClaudeProvider(model=model_name)
    elif provider_name == "openai":
        return OpenAIProvider(model=model_name)
    else:
        return OllamaProvider(model=model_name)
