"""Google Gemini provider using google-genai SDK."""

import logging
import time

from google import genai
from google.genai import types
from google.genai.errors import ServerError

from models.base import BaseProvider, LLMResponse, Message

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

log = logging.getLogger(__name__)


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
    ) -> LLMResponse:
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
                include_thoughts=True,
            )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=contents,
                    config=config,
                )
                break
            except ServerError as e:
                if attempt < MAX_RETRIES:
                    log.warning("Gemini ServerError (attempt %d/%d): %s", attempt, MAX_RETRIES, e)
                    time.sleep(RETRY_DELAY * attempt)
                else:
                    raise

        text = ""
        thinking_text = None
        thinking_parts = []
        for part in response.candidates[0].content.parts:
            if getattr(part, "thought", False):
                thinking_parts.append(part.text)
            elif part.text:
                text = part.text
        if thinking_parts:
            thinking_text = "\n".join(thinking_parts)

        return LLMResponse(text=text, reasoning=thinking_text)
