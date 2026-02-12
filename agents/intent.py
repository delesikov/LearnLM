"""Intent selection and prompt composition for the student agent."""

import logging
import random
from pathlib import Path

from models.base import BaseProvider, Message

log = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

DEFAULT_CLASSIFIER_TEMPLATE = (
    (_PROMPTS_DIR / "intent_classifier.md").read_text(encoding="utf-8").strip()
)
_ANSWER_CORRECT_PROMPT = (
    (_PROMPTS_DIR / "intent_answer_correct.md").read_text(encoding="utf-8").strip()
)
_ANSWER_WRONG_PROMPT = (
    (_PROMPTS_DIR / "intent_answer_wrong.md").read_text(encoding="utf-8").strip()
)


def pick_intent(intent_weights: dict[str, int], intent_prompts: dict[str, str]) -> tuple[str, str]:
    """Select a random intent based on weights.

    Returns (intent_id, intent_prompt).
    """
    ids = list(intent_weights.keys())
    weights = [intent_weights[i] for i in ids]
    chosen_id = random.choices(ids, weights=weights, k=1)[0]
    return chosen_id, intent_prompts[chosen_id]


def pick_intent_llm(
    provider: BaseProvider,
    history: list[Message],
    intent_names: dict[str, str],
    intent_prompts: dict[str, str],
    intent_weights: dict[str, int],
    student_type: str,
    classifier_template: str = "",
) -> tuple[str, str]:
    """Use LLM to select a context-aware intent.

    Falls back to random selection if LLM response can't be parsed.
    Returns (intent_id, intent_prompt).
    """
    template = classifier_template or DEFAULT_CLASSIFIER_TEMPLATE

    # Build intents list for the classifier prompt
    total = sum(intent_weights.values()) or 1
    lines = []
    for iid, name in intent_names.items():
        w = intent_weights.get(iid, 0)
        if w > 0:
            pct = round(w / total * 100)
            lines.append(f"- {iid} ({pct}%) — {name}")

    intents_list = "\n".join(lines)
    system_prompt = template.format(
        student_type=student_type,
        intents_list=intents_list,
    )

    # Classifier only needs recent context, not the full dialog
    recent_history = history[-10:]

    try:
        result = provider.generate_response(
            system_prompt=system_prompt,
            history=recent_history,
            temperature=0.3,
            max_tokens=50,
        )
        raw = result.text
        chosen_id = raw.strip().lower().strip(".,!\"'` \n")
        if chosen_id in intent_prompts:
            log.info("LLM chose intent: %s", chosen_id)
            return chosen_id, intent_prompts[chosen_id]

        log.warning("LLM returned unknown intent '%s', falling back to random", raw.strip())
    except Exception:
        log.exception("LLM intent selection failed, falling back to random")

    return pick_intent(intent_weights, intent_prompts)


def build_student_prompt(
    base_prompt: str, intent_id: str, intent_prompt: str, correct_answer_prob: int = 50
) -> str:
    """Combine student base prompt with the current intent prompt.

    For the 'answer' intent, a random roll determines whether the student
    should answer correctly or make a mistake, based on *correct_answer_prob*.
    """
    # Intent goes FIRST so the model sees the directive before the character description.
    intent_block = f"⚠️ ЗАДАЧА НА ЭТОТ ХОД:\n{intent_prompt}"

    if intent_id == "answer":
        if random.randint(1, 100) <= correct_answer_prob:
            intent_block += f"\n\n{_ANSWER_CORRECT_PROMPT}"
        else:
            intent_block += f"\n\n{_ANSWER_WRONG_PROMPT}"

    return f"{intent_block}\n\n---\n\n{base_prompt}"
