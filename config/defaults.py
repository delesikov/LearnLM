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
# Used for "random" intent mode only.

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

# ─── Mistake types (for "answer" intent, wrong-answer branch) ────

MISTAKE_TYPES = [
    {
        "id": "careless",
        "name": "Невнимательность",
        "description": "Невнимательность — почти правильно, одна маленькая ошибка: не тот знак, не та цифра, потерял минус при переносе. Сам не замечаешь.",
    },
    {
        "id": "procedure",
        "name": "Незнание процедуры",
        "description": "Незнание процедуры — общее направление верное, но конкретный шаг делаешь неверно. Знаешь что надо раскрыть скобки, но раскрываешь неправильно.",
    },
    {
        "id": "method",
        "name": "Незнание способа",
        "description": "Незнание способа — не знаешь алгоритм целиком, начинаешь с неверного шага или применяешь метод не к той задаче. Например: решаешь квадратное уравнение подбором.",
    },
    {
        "id": "unstable_proc",
        "name": "Неустойчивая процедура",
        "description": "Неустойчивое знание процедуры — раньше делал правильно, сейчас ошибся. Применяешь правило неверно, хотя знаешь его. Ошибка непоследовательная.",
    },
    {
        "id": "unstable_method",
        "name": "Неустойчивый способ",
        "description": "Неустойчивое знание способа — знаешь алгоритм в целом, но применяешь хаотично: пропускаешь шаг, путаешь порядок действий.",
    },
    {
        "id": "misconception",
        "name": "Неверная концепция",
        "description": "Неверная концепция — уверен что прав, но ошибаешься систематически из-за неверного правила в голове. Например: думаешь что (a+b)^2 = a^2+b^2. Не сомневаешься.",
    },
]

# Per student type. Слабый: много незнания способа/процедуры.
# Средний: неустойчивые знания. Сильный: в основном невнимательность.
DEFAULT_MISTAKE_WEIGHTS: dict[str, dict[str, int]] = {
    "Слабый": {
        "careless": 5,
        "procedure": 30,
        "method": 35,
        "unstable_proc": 15,
        "unstable_method": 10,
        "misconception": 5,
    },
    "Средний": {
        "careless": 15,
        "procedure": 20,
        "method": 20,
        "unstable_proc": 20,
        "unstable_method": 15,
        "misconception": 10,
    },
    "Сильный": {
        "careless": 40,
        "procedure": 10,
        "method": 5,
        "unstable_proc": 25,
        "unstable_method": 15,
        "misconception": 5,
    },
}

# ─── Situations (for LLM intent mode) ────────────────────────────
# Each situation maps to a distribution of intent weights (sum = 100).

SITUATIONS = [
    {"id": "math_question",      "name": "Математический вопрос"},
    {"id": "step_by_step",       "name": "Ведёт по шагам"},
    {"id": "plan_with_question", "name": "План + первый вопрос"},
    {"id": "plan_approval",      "name": "План + «согласен?»"},
    {"id": "explanation",        "name": "Объяснение теории"},
    {"id": "correction",         "name": "Указал ошибку / подсказка"},
    {"id": "praise",             "name": "Похвалил / подтвердил"},
    {"id": "comprehension_check","name": "Вопрос на понимание"},
    {"id": "counterexample",     "name": "Контрпример"},
    {"id": "task_solved",        "name": "Задача решена"},
    {"id": "offtopic",           "name": "Офтопик"},
    {"id": "alternative_method", "name": "Альтернативный подход"},
]

_Z = {  # zero weights for all intents (template)
    "chat": 0, "set-problem": 0, "answer": 0, "get-explanation": 0,
    "thank-tutor": 0, "agree-with-tutor": 0, "find-mistake": 0,
    "criticize-tutor": 0, "end-dialog": 0, "get-solution": 0,
}

# Situation weights per student type.
# Each situation's weights must sum to 100.
# Слабый: неуверен, часто просит объяснений или готовый ответ.
# Средний: сбалансирован.
# Сильный: уверен, охотно отвечает, чаще критикует и хочет ещё задач.
DEFAULT_SITUATION_WEIGHTS: dict[str, dict[str, dict[str, int]]] = {
    "Слабый": {
        "math_question":       {**_Z, "answer": 50, "get-explanation": 30, "get-solution": 20},
        "step_by_step":        {**_Z, "answer": 55, "get-explanation": 30, "get-solution": 15},
        "plan_with_question":  {**_Z, "answer": 35, "agree-with-tutor": 35, "get-explanation": 30},
        "plan_approval":       {**_Z, "agree-with-tutor": 65, "get-explanation": 25, "criticize-tutor": 10},
        "explanation":         {**_Z, "agree-with-tutor": 40, "get-explanation": 45, "answer": 10, "chat": 5},
        "correction":          {**_Z, "answer": 50, "get-explanation": 25, "get-solution": 20, "chat": 5},
        "praise":              {**_Z, "answer": 50, "agree-with-tutor": 40, "chat": 10},
        "comprehension_check": {**_Z, "answer": 55, "get-explanation": 45},
        "counterexample":      {**_Z, "answer": 45, "get-explanation": 50, "chat": 5},
        "task_solved":         {**_Z, "thank-tutor": 50, "end-dialog": 30, "set-problem": 20},
        "offtopic":            {**_Z, "chat": 65, "set-problem": 25, "answer": 10},
        "alternative_method":  {**_Z, "agree-with-tutor": 65, "get-explanation": 30, "criticize-tutor": 5},
    },
    "Средний": {
        "math_question":       {**_Z, "answer": 65, "get-explanation": 25, "get-solution": 10},
        "step_by_step":        {**_Z, "answer": 70, "get-explanation": 20, "get-solution": 10},
        "plan_with_question":  {**_Z, "answer": 45, "agree-with-tutor": 35, "get-explanation": 20},
        "plan_approval":       {**_Z, "agree-with-tutor": 70, "get-explanation": 20, "criticize-tutor": 10},
        "explanation":         {**_Z, "agree-with-tutor": 50, "get-explanation": 35, "answer": 15},
        "correction":          {**_Z, "answer": 65, "get-explanation": 25, "get-solution": 10},
        "praise":              {**_Z, "answer": 55, "agree-with-tutor": 35, "chat": 10},
        "comprehension_check": {**_Z, "answer": 70, "get-explanation": 30},
        "counterexample":      {**_Z, "answer": 60, "get-explanation": 40},
        "task_solved":         {**_Z, "thank-tutor": 50, "end-dialog": 30, "set-problem": 20},
        "offtopic":            {**_Z, "chat": 55, "set-problem": 30, "answer": 15},
        "alternative_method":  {**_Z, "agree-with-tutor": 55, "get-explanation": 35, "criticize-tutor": 10},
    },
    "Сильный": {
        "math_question":       {**_Z, "answer": 75, "get-explanation": 15, "find-mistake": 10},
        "step_by_step":        {**_Z, "answer": 75, "get-explanation": 15, "find-mistake": 10},
        "plan_with_question":  {**_Z, "answer": 55, "agree-with-tutor": 35, "get-explanation": 10},
        "plan_approval":       {**_Z, "agree-with-tutor": 60, "get-explanation": 20, "criticize-tutor": 20},
        "explanation":         {**_Z, "agree-with-tutor": 60, "get-explanation": 25, "answer": 15},
        "correction":          {**_Z, "answer": 75, "get-explanation": 15, "find-mistake": 10},
        "praise":              {**_Z, "answer": 60, "agree-with-tutor": 35, "chat": 5},
        "comprehension_check": {**_Z, "answer": 85, "get-explanation": 15},
        "counterexample":      {**_Z, "answer": 75, "get-explanation": 25},
        "task_solved":         {**_Z, "thank-tutor": 40, "end-dialog": 20, "set-problem": 40},
        "offtopic":            {**_Z, "chat": 45, "set-problem": 35, "answer": 20},
        "alternative_method":  {**_Z, "agree-with-tutor": 45, "get-explanation": 35, "criticize-tutor": 20},
    },
}
