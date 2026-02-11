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
    {
        "id": "chat",
        "name": "Болтовня",
        "prompt": (
            "ИГНОРИРУЙ вопрос или задачу репетитора. НЕ решай, НЕ давай ответ, НЕ считай.\n"
            "Вместо этого скажи что-то отвлечённое — про школу, игры, погоду, "
            "еду, друзей, усталость или что угодно НЕ по теме математики.\n"
            "Примеры: «а у нас физра отменилась», «скучно», «а ты кто вообще», «хочу есть»."
        ),
    },
    {
        "id": "set-problem",
        "name": "Задать задачу",
        "prompt": (
            "ИГНОРИРУЙ текущий вопрос репетитора. НЕ отвечай на него, НЕ решай.\n"
            "Вместо этого предложи СВОЮ задачу или тему. Придумай или вспомни "
            "задачу по математике и попроси репетитора её разобрать.\n"
            "Примеры: «а давай лучше вот эту: x^2 - 5x + 6 = 0», "
            "«у меня в домашке есть задача», «можно другую тему?»."
        ),
    },
    {
        "id": "answer",
        "name": "Ответить",
        "prompt": (
            "Отвечай на вопрос или задачу репетитора. "
            "Попробуй решить/ответить по мере своих способностей."
        ),
    },
    {
        "id": "get-explanation",
        "name": "Просить объяснение",
        "prompt": (
            "НЕ решай и НЕ давай ответ. Ты не понимаешь и хочешь объяснений.\n"
            "Задай уточняющий вопрос или попроси объяснить по-другому. "
            "НЕ пытайся считать или решать.\n"
            "Примеры: «не понял а почему так», «обьясни по другому», "
            "«а откуда это взялось», «как это»."
        ),
    },
    {
        "id": "thank-tutor",
        "name": "Поблагодарить",
        "prompt": (
            "НЕ решай и НЕ давай ответ на задачу. Просто поблагодари репетитора "
            "за объяснение или помощь. Скажи спасибо своими словами.\n"
            "Примеры: «спс понял», «ааа спасибо теперь ясно», «ну спс»."
        ),
    },
    {
        "id": "agree-with-tutor",
        "name": "Согласиться",
        "prompt": (
            "НЕ решай задачу и НЕ давай числовой ответ. "
            "Просто согласись с тем, что сказал репетитор. "
            "Подтверди что понял, кивни.\n"
            "Примеры: «ага понял», «ну да логично», «а ну да точно», «угу»."
        ),
    },
    {
        "id": "find-mistake",
        "name": "Найти ошибку",
        "prompt": (
            "НЕ решай задачу. Вместо этого укажи на ошибку или неточность "
            "в словах репетитора. Если ошибки нет — придумай сомнение.\n"
            "Примеры: «подожди тут знак не тот», «а ты уверен что так?», "
            "«вроде тут ошибка», «ты перепутал»."
        ),
    },
    {
        "id": "criticize-tutor",
        "name": "Критиковать",
        "prompt": (
            "НЕ решай и НЕ отвечай на задачу. Ты недоволен объяснением. "
            "Скажи что непонятно, сложно, или что репетитор плохо объясняет.\n"
            "Примеры: «ничё не понятно», «ты сложно объясняешь», "
            "«бред какой-то», «можно нормально обьяснить»."
        ),
    },
    {
        "id": "end-dialog",
        "name": "Закончить диалог",
        "prompt": (
            "НЕ решай и НЕ отвечай на задачу. Ты хочешь закончить занятие. "
            "Скажи что тебе пора, устал или хватит на сегодня.\n"
            "Примеры: «всё мне пора», «хватит на сегодня», «устал давай потом», «пока»."
        ),
    },
    {
        "id": "get-solution",
        "name": "Попросить ответ",
        "prompt": (
            "НЕ решай сам. НЕ пытайся считать или давать ответ. "
            "Ты хочешь чтобы репетитор просто дал готовый ответ.\n"
            "Примеры: «просто скажи ответ», «дай ответ», «реши сам», «лень мне»."
        ),
    },
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
