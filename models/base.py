"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str


class BaseProvider(ABC):
    @abstractmethod
    def generate_response(
        self,
        system_prompt: str,
        history: list[Message],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate a response given system prompt and conversation history."""
        ...
