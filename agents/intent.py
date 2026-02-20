"""Intent selection and prompt composition for the student agent."""

import logging
import random
from pathlib import Path

from config.defaults import MISTAKE_TYPES
from models.base import BaseProvider, Message

log = logging.getLogger(__name__)

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

DEFAULT_CLASSIFIER_TEMPLATE = (
    (_PROMPTS_DIR / "intent_classifier.md").read_text(encoding="utf-8").strip()
)
_ANSWER_CORRECT_PROMPT = (
    (_PROMPTS_DIR / "intent_answer_correct.md").read_text(encoding="utf-8").strip()
)
_ANSWER_WRONG_TEMPLATE = (
    (_PROMPTS_DIR / "intent_answer_wrong.md").read_text(encoding="utf-8").strip()
)



def pick_mistake(mistake_weights: dict[str, int]) -> dict:
    """Pick a mistake type by weights. Returns one MISTAKE_TYPES entry."""
    ids = [m["id"] for m in MISTAKE_TYPES]
    weights = [mistake_weights.get(mid, 0) for mid in ids]
    if sum(weights) == 0:
        weights = [1] * len(ids)
    chosen_id = random.choices(ids, weights=weights, k=1)[0]
    return next(m for m in MISTAKE_TYPES if m["id"] == chosen_id)


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
    situation_weights: dict[str, dict[str, int]],
    intent_prompts: dict[str, str],
    classifier_template: str = "",
) -> tuple[str, str]:
    """Use LLM to classify the teacher's situation, then pick intent by situation weights.

    LLM returns a single situation_id → lookup situation_weights[situation_id]
    → weighted random.choices() among intents with weight > 0.
    Falls back to aggregate weights across all situations if LLM response can't be parsed.
    Returns (intent_id, intent_prompt).
    """
    template = classifier_template or DEFAULT_CLASSIFIER_TEMPLATE

    # Classifier only needs recent context, not the full dialog
    recent_history = history[-10:]

    try:
        result = provider.generate_response(
            system_prompt=template,
            history=recent_history,
            temperature=0.3,
            max_tokens=30,
        )
        situation_id = result.text.strip().lower().strip(".,!\"'` \n")

        if situation_id in situation_weights:
            weights = situation_weights[situation_id]
            valid = {iid: w for iid, w in weights.items() if w > 0 and iid in intent_prompts}
            if valid:
                ids = list(valid.keys())
                wts = [valid[iid] for iid in ids]
                chosen_id = random.choices(ids, weights=wts, k=1)[0]
                log.info("Situation: %s → intent: %s", situation_id, chosen_id)
                return chosen_id, intent_prompts[chosen_id]

        log.warning("LLM returned unknown situation '%s', falling back to aggregate", situation_id)
    except Exception:
        log.exception("LLM intent selection failed, falling back to aggregate")

    # Fallback: aggregate weights across all situations → weighted random
    agg: dict[str, int] = {}
    for sit_weights in situation_weights.values():
        for iid, w in sit_weights.items():
            if iid in intent_prompts:
                agg[iid] = agg.get(iid, 0) + w
    return pick_intent(agg, intent_prompts)


def build_student_prompt(
    base_prompt: str,
    intent_id: str,
    intent_prompt: str,
    correct_answer_prob: int = 50,
    mistake_weights: dict[str, int] | None = None,
) -> str:
    """Combine student base prompt with the current intent prompt.

    For the 'answer' intent, a random roll determines whether the student
    should answer correctly or make a mistake, based on *correct_answer_prob*.
    When wrong, a mistake type is picked by *mistake_weights* and injected
    into the prompt template.
    """
    # Intent goes FIRST so the model sees the directive before the character description.
    intent_block = f"⚠️ ЗАДАЧА НА ЭТОТ ХОД:\n{intent_prompt}"

    if intent_id == "answer":
        if random.randint(1, 100) <= correct_answer_prob:
            intent_block += f"\n\n{_ANSWER_CORRECT_PROMPT}"
        else:
            mistake = pick_mistake(mistake_weights or {})
            log.info("Mistake type: %s", mistake["id"])
            wrong_prompt = _ANSWER_WRONG_TEMPLATE.format(
                mistake_description=mistake["description"]
            )
            intent_block += f"\n\n{wrong_prompt}"

    return f"{intent_block}\n\n---\n\n{base_prompt}"
