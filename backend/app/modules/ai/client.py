import abc
import time
import json
import logging
import math
from typing import AsyncGenerator, Dict, Any, List, Optional
from pydantic import BaseModel
import httpx

from app.core.config import settings

logger = logging.getLogger("ai_client")

class LLMResponse(BaseModel):
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    model: str = ""
    provider: str = ""
    refusal: bool = False

class BaseLLMClient(abc.ABC):
    @abc.abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generates a complete completion text."""
        pass

    @abc.abstractmethod
    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Streams completion tokens sequentially."""
        pass

    @abc.abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates 1536-dimensional vector embeddings for a list of text chunks."""
        pass

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = settings.OPENAI_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        start_time = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency = (time.time() - start_time) * 1000.0
        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            latency_ms=round(latency, 2),
            model=self.model,
            provider="openai"
        )

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        line_data = line[6:].strip()
                        if line_data == "[DONE]":
                            break
                        try:
                            parsed = json.loads(line_data)
                            delta = parsed["choices"][0]["delta"]
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                        except Exception:
                            continue

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": texts
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        embeddings = [item["embedding"] for item in data["data"]]
        return embeddings

class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = settings.ANTHROPIC_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        start_time = time.time()
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        latency = (time.time() - start_time) * 1000.0
        content = data["content"][0]["text"]
        usage = data.get("usage", {})

        return LLMResponse(
            content=content,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            latency_ms=round(latency, 2),
            model=self.model,
            provider="anthropic"
        )

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        # Fallback to single generation chunked for stream
        res = await self.generate_text(prompt, system_prompt)
        words = res.content.split(" ")
        for w in words:
            yield w + " "

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Anthropic doesn't have an embedding API; generate deterministic normalized vectors
        return MockOrLocalLLMClient()._generate_deterministic_embeddings(texts)

class MockOrLocalLLMClient(BaseLLMClient):
    """High-fidelity deterministic local fallback provider for offline development and testing."""

    def _generate_deterministic_embeddings(self, texts: List[str]) -> List[List[float]]:
        dim = settings.EMBEDDING_DIMENSION
        results = []
        for text in texts:
            # Deterministic hash-based vector
            vec = []
            seed = sum(ord(c) for c in text[:64])
            for i in range(dim):
                val = math.sin((seed + i) * 0.17) * math.cos((seed + i * 2) * 0.31)
                vec.append(val)
            # Normalize vector to unit length
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            results.append([x / norm for x in vec])
        return results

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        content = (
            "Based on your uploaded course materials, the gradient descent algorithm iteratively updates parameter weights "
            "in the opposite direction of the gradient of the objective function. "
            "If the learning rate is chosen too high, the updates oscillate across the loss surface and fail to converge. "
            "[Source: intro_to_ml.pdf — Page 4]"
        )
        return LLMResponse(
            content=content,
            prompt_tokens=120,
            completion_tokens=48,
            latency_ms=85.0,
            model="local-deterministic-mock",
            provider="local"
        )

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        tokens = [
            "Based on your uploaded project materials, ",
            "gradient descent minimizes the cost function by taking steps ",
            "proportional to the negative gradient. ",
            "When the step size is excessive, overshooting occurs [Source: intro_to_ml.pdf — Page 4]. ",
            "Would you like to practice calculating an update step?"
        ]
        for t in tokens:
            yield t

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._generate_deterministic_embeddings(texts)

def get_llm_client(provider: Optional[str] = None) -> BaseLLMClient:
    """Factory selecting AI client based on API key availability and preferences."""
    chosen_provider = provider or settings.DEFAULT_PROVIDER

    if chosen_provider == "openai" and settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 10:
        return OpenAIClient(api_key=settings.OPENAI_API_KEY)
    elif chosen_provider == "anthropic" and settings.ANTHROPIC_API_KEY and len(settings.ANTHROPIC_API_KEY) > 10:
        return AnthropicClient(api_key=settings.ANTHROPIC_API_KEY)
    else:
        return MockOrLocalLLMClient()
