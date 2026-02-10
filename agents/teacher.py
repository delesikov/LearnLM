"""Teacher agent logic."""

from models.base import BaseProvider, Message


class TeacherAgent:
    def __init__(self, provider: BaseProvider, system_prompt: str):
        self.provider = provider
        self.system_prompt = system_prompt

    def generate(
        self,
        history: list[Message],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate teacher response.

        History is from the teacher's perspective:
        teacher = assistant, student = user.
        """
        return self.provider.generate_response(
            system_prompt=self.system_prompt,
            history=history,
            temperature=temperature,
            max_tokens=max_tokens,
        )
