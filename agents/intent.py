"""Intent selection and prompt composition for the student agent."""

import random


def pick_intent(intent_weights: dict[str, int], intent_prompts: dict[str, str]) -> tuple[str, str]:
    """Select a random intent based on weights.

    Returns (intent_id, intent_prompt).
    """
    ids = list(intent_weights.keys())
    weights = [intent_weights[i] for i in ids]
    chosen_id = random.choices(ids, weights=weights, k=1)[0]
    return chosen_id, intent_prompts[chosen_id]


def build_student_prompt(base_prompt: str, intent_prompt: str) -> str:
    """Combine student base prompt with the current intent prompt."""
    return f"{base_prompt}\n\n--- Текущее намерение ---\n{intent_prompt}"
