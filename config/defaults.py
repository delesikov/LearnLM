"""Default prompts, models, and intent configurations."""

from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    return (_PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


# ─── Available models ───────────────────────────────────────────────

AVAILABLE_MODELS = {
    "Gemini 2.5 Flash": {
        "provider": "gemini",
        "model_id": "gemini-2.5-flash",
        "supports_thinking": False,
        "supports_reasoning": False,
    },
    "Gemini 3 Flash": {
        "provider": "gemini",
        "model_id": "gemini-3-flash-preview",
        "supports_thinking": True,
        "supports_reasoning": False,
    },
    "GPT OSS 120B (Yandex)": {
        "provider": "yandex",
        "model_id": "gpt-oss-120b/latest",
        "supports_thinking": False,
        "supports_reasoning": True,
    },
}

THINKING_LEVELS = [None, "minimal", "low", "medium", "high"]
REASONING_EFFORTS = [None, "low", "medium", "high"]

# ─── Student types ──────────────────────────────────────────────────

STUDENT_TYPES = ["Слабый", "Средний", "Сильный"]

# ─── Default teacher prompt ─────────────────────────────────────────

DEFAULT_TEACHER_PROMPT = _load_prompt("teacher.md")

# ─── Default student prompts (per type) ─────────────────────────────

DEFAULT_STUDENT_PROMPTS = {
    "Слабый": _load_prompt("student_weak.md"),
    "Средний": _load_prompt("student_medium.md"),
    "Сильный": _load_prompt("student_strong.md"),
}


# ─── Static teacher greeting (shown immediately on app load) ────────

TEACHER_GREETING = (
    "Добро пожаловать в режим обучения!\n\n"
    "Не буду давать готовые ответы — помогу понять через правильные вопросы.\n\n"
    "Что изучаем?\n"
    "- Задачу, которая не решается\n"
    "- Тему, которая непонятна\n"
    "- Что-то из домашки\n\n"
    "Пиши, начнём! 👇"
)

# ─── Intents ────────────────────────────────────────────────────────

INTENTS = [
    {"id": "chat", "name": "Болтовня", "prompt": _load_prompt("intent_chat.md")},
    {"id": "set-problem", "name": "Задать задачу", "prompt": _load_prompt("intent_set_problem.md")},
    {"id": "answer", "name": "Ответить", "prompt": _load_prompt("intent_answer.md")},
    {"id": "get-explanation", "name": "Просить объяснение", "prompt": _load_prompt("intent_get_explanation.md")},
    {"id": "thank-tutor", "name": "Поблагодарить", "prompt": _load_prompt("intent_thank_tutor.md")},
    {"id": "agree-with-tutor", "name": "Согласиться", "prompt": _load_prompt("intent_agree_with_tutor.md")},
    {"id": "find-mistake", "name": "Найти ошибку", "prompt": _load_prompt("intent_find_mistake.md")},
    {"id": "criticize-tutor", "name": "Критиковать", "prompt": _load_prompt("intent_criticize_tutor.md")},
    {"id": "end-dialog", "name": "Закончить диалог", "prompt": _load_prompt("intent_end_dialog.md")},
    {"id": "get-solution", "name": "Попросить ответ", "prompt": _load_prompt("intent_get_solution.md")},
]

# ─── Default intent weights per student type (must sum to 100) ──────

_REAL_WEIGHTS = {
    "chat": 5,
    "set-problem": 14,
    "answer": 58,
    "get-explanation": 4,
    "thank-tutor": 0,
    "agree-with-tutor": 12,
    "find-mistake": 1,
    "criticize-tutor": 3,
    "end-dialog": 1,
    "get-solution": 2,
}

DEFAULT_INTENT_WEIGHTS = {
    "Слабый": _REAL_WEIGHTS.copy(),
    "Средний": _REAL_WEIGHTS.copy(),
    "Сильный": _REAL_WEIGHTS.copy(),
}

# ─── Probability of correct answer (for "answer" intent) ─────────

DEFAULT_CORRECT_ANSWER_PROB = {
    "Слабый": 20,
    "Средний": 50,
    "Сильный": 80,
}
