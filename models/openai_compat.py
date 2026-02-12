"""Yandex Cloud provider using OpenAI-compatible Responses API."""

import openai

from config.settings import YANDEX_BASE_URL
from models.base import BaseProvider, LLMResponse, Message


class OpenAICompatProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        folder_id: str,
        model_id: str,
        reasoning_effort: str | None = None,
    ):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=YANDEX_BASE_URL,
            project=folder_id,
        )
        self.model_uri = f"gpt://{folder_id}/{model_id}"
        self.reasoning_effort = reasoning_effort

    def generate_response(
        self,
        system_prompt: str,
        history: list[Message],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        input_messages = []
        for msg in history:
            if msg.content.strip():
                input_messages.append({"role": msg.role, "content": msg.content})

        if not input_messages:
            input_messages.append({"role": "user", "content": "Начни диалог."})

        kwargs = {
            "model": self.model_uri,
            "instructions": system_prompt,
            "input": input_messages,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        if self.reasoning_effort:
            kwargs["reasoning"] = {"effort": self.reasoning_effort}

        response = self.client.responses.create(**kwargs)

        reasoning_text = None
        for item in response.output:
            if item.type == "reasoning":
                parts = []
                for s in getattr(item, "summary", []):
                    if hasattr(s, "text"):
                        parts.append(s.text)
                if parts:
                    reasoning_text = "\n".join(parts)

        return LLMResponse(text=response.output_text, reasoning=reasoning_text)
