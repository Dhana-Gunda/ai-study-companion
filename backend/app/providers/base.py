from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List

class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM Providers (Ollama, Claude, OpenAI)."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        """Stream generated tokens from the LLM provider."""
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check provider connectivity and model availability."""
        pass
