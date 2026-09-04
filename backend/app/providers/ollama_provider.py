import httpx
import json
import logging
from typing import AsyncGenerator, Dict, Any, List
from .base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger("lenny_assistant.providers.ollama")

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": 4096
            }
        }

        url = f"{self.base_url}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code == 404:
                        yield f"Error: Model '{self.model}' not found on Ollama. Please run: `ollama pull {self.model}` in your terminal."
                        return
                    elif response.status_code != 200:
                        error_detail = await response.aread()
                        yield f"Ollama API error (HTTP {response.status_code}): {error_detail.decode('utf-8', errors='ignore')}"
                        return

                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                content = chunk.get("message", {}).get("content", "")
                                if content:
                                    yield content
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue

        except httpx.ConnectError:
            yield (
                f"\n\n> [!WARNING]\n"
                f"> **Ollama Connection Failed**: Could not connect to Ollama at `{self.base_url}`.\n"
                f"> Please ensure Ollama is running (`ollama serve`) and model is installed (`ollama pull {self.model}`).\n"
                f"> Alternatively, select Claude or OpenAI from the model switcher in the navigation bar."
            )
        except httpx.TimeoutException:
            yield f"\n\nError: Request to Ollama model '{self.model}' timed out after 120 seconds."
        except Exception as e:
            logger.error(f"Unexpected Ollama exception: {e}", exc_info=True)
            yield f"\n\nUnexpected error communicating with Ollama: {str(e)}"

    async def check_health(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return {
                        "connected": True,
                        "base_url": self.base_url,
                        "active_model": self.model,
                        "available_models": models
                    }
                return {"connected": False, "error": f"HTTP {res.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e), "base_url": self.base_url}
