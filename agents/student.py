"""Student agent logic with intent system."""

from agents.intent import pick_intent, build_student_prompt
from models.base import BaseProvider, Message


class StudentAgent:
    def __init__(self, provider: BaseProvider, base_prompt: str):
        self.provider = provider
        self.base_prompt = base_prompt

    def generate(
        self,
        history: list[Message],
        intent_weights: dict[str, int],
        intent_prompts: dict[str, str],
        temperature: float,
        max_tokens: int,
    ) -> tuple[str, str]:
        """Generate student response with intent selection.

        History is from the student's perspective:
        student = assistant, teacher = user (roles are flipped).

        Returns (response_text, intent_id).
        """
        intent_id, intent_prompt = pick_intent(intent_weights, intent_prompts)
        system_prompt = build_student_prompt(self.base_prompt, intent_prompt)

        response = self.provider.generate_response(
            system_prompt=system_prompt,
            history=history,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response, intent_id
