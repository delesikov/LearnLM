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


def build_student_prompt(
    base_prompt: str, intent_id: str, intent_prompt: str, correct_answer_prob: int = 50
) -> str:
    """Combine student base prompt with the current intent prompt.

    For the 'answer' intent, a random roll determines whether the student
    should answer correctly or make a mistake, based on *correct_answer_prob*.
    """
    parts = [base_prompt, f"\n\n--- Текущее намерение ---\n{intent_prompt}"]

    if intent_id == "answer":
        if random.randint(1, 100) <= correct_answer_prob:
            parts.append("\n\n--- Точность ---\nОтветь ПРАВИЛЬНО. Дай верный ответ.")
        else:
            parts.append(
                "\n\n--- Точность ---\nДопусти ОШИБКУ. Дай неправильный ответ — "
                "перепутай знак, посчитай неверно или примени не ту формулу."
            )

    return "".join(parts)
