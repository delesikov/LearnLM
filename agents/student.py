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
        situation_weights: dict[str, dict[str, int]] | None = None,
        classifier_template: str = "",
        mistake_weights: dict[str, int] | None = None,
    ) -> tuple[LLMResponse, str]:
        """Generate student response with intent selection.

        intent_mode: "random" (weighted random from intent_weights)
                  or "llm" (LLM classifies teacher situation → situation_weights lookup).

        Returns (LLMResponse, intent_id).
        """
        if intent_mode == "llm" and situation_weights:
            intent_id, intent_prompt = pick_intent_llm(
                provider=self.provider,
                history=history,
                situation_weights=situation_weights,
                intent_prompts=intent_prompts,
                classifier_template=classifier_template,
            )
        else:
            intent_id, intent_prompt = pick_intent(intent_weights, intent_prompts)

        system_prompt = build_student_prompt(
            self.base_prompt, intent_id, intent_prompt, correct_answer_prob, mistake_weights
        )

        llm_response = self.provider.generate_response(
            system_prompt=system_prompt,
            history=history,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return llm_response, intent_id
