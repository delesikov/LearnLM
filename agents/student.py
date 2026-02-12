"""Student agent logic with intent system."""

from agents.intent import pick_intent, pick_intent_llm, build_student_prompt
from models.base import BaseProvider, LLMResponse, Message


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
        correct_answer_prob: int = 50,
        intent_mode: str = "random",
        intent_names: dict[str, str] | None = None,
        student_type: str = "",
        classifier_template: str = "",
    ) -> tuple[LLMResponse, str]:
        """Generate student response with intent selection.

        intent_mode: "random" (weighted random) or "llm" (LLM classifier).

        Returns (LLMResponse, intent_id).
        """
        if intent_mode == "llm" and intent_names:
            intent_id, intent_prompt = pick_intent_llm(
                provider=self.provider,
                history=history,
                intent_names=intent_names,
                intent_prompts=intent_prompts,
                intent_weights=intent_weights,
                student_type=student_type,
                classifier_template=classifier_template,
            )
        else:
            intent_id, intent_prompt = pick_intent(intent_weights, intent_prompts)

        system_prompt = build_student_prompt(
            self.base_prompt, intent_id, intent_prompt, correct_answer_prob
        )

        llm_response = self.provider.generate_response(
            system_prompt=system_prompt,
            history=history,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return llm_response, intent_id
