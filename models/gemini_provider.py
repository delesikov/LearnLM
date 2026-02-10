"""Google Gemini provider using google-genai SDK."""

from google import genai
from google.genai import types

from models.base import BaseProvider, Message


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str, model_id: str, thinking_level: str | None = None):
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id
        self.thinking_level = thinking_level

    def generate_response(
        self,
        system_prompt: str,
        history: list[Message],
        temperature: float,
        max_tokens: int,
    ) -> str:
        contents = []
        for msg in history:
            role = "model" if msg.role == "assistant" else "user"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg.content)]))

        if not contents:
            contents.append(types.Content(role="user", parts=[types.Part(text="Начни диалог.")]))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        if self.thinking_level:
            config.thinking_config = types.ThinkingConfig(
                thinking_level=self.thinking_level,
            )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config,
        )

        for part in response.candidates[0].content.parts:
            if part.text:
                return part.text
        return ""
