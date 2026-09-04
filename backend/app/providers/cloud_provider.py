import httpx
import json
import logging
from typing import AsyncGenerator, Dict, Any, List
from .base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger("lenny_assistant.providers.cloud")

class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield (
                "\n\n> [!CAUTION]\n"
                "> **Anthropic API Key Missing**: Please set `ANTHROPIC_API_KEY` in your `.env` file.\n"
                "> Or toggle to the local **Ollama** model using the provider selector in the top navbar."
            )
            return

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        # Convert standard message format to Anthropic format
        anthropic_messages = []
        for msg in messages:
            role = msg.get("role")
            if role in ["user", "assistant"]:
                anthropic_messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })

        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": anthropic_messages,
            "max_tokens": 4096,
            "temperature": temperature,
            "stream": True
        }

        url = "https://api.anthropic.com/v1/messages"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        yield f"Anthropic API Error (HTTP {response.status_code}): {error_body.decode('utf-8', errors='ignore')}"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                event_type = data.get("type")
                                if event_type == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        yield delta.get("text", "")
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Claude API exception: {e}", exc_info=True)
            yield f"Error communicating with Anthropic Claude: {str(e)}"

    async def check_health(self) -> Dict[str, Any]:
        return {
            "provider": "anthropic",
            "configured": bool(self.api_key),
            "model": self.model
        }


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield (
                "\n\n> [!CAUTION]\n"
                "> **OpenAI API Key Missing**: Please set `OPENAI_API_KEY` in your `.env` file.\n"
                "> Or toggle to the local **Ollama** model using the provider selector in the top navbar."
            )
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        openai_messages = [{"role": "system", "content": system_prompt}] + messages
        payload = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": 4096,
            "stream": True
        }

        url = "https://api.openai.com/v1/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        yield f"OpenAI API Error (HTTP {response.status_code}): {error_body.decode('utf-8', errors='ignore')}"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"OpenAI API exception: {e}", exc_info=True)
            yield f"Error communicating with OpenAI: {str(e)}"

    async def check_health(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "configured": bool(self.api_key),
            "model": self.model
        }
