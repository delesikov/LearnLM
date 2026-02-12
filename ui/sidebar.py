"""Sidebar: API keys, model selection, prompts, intents, generation params."""

import copy

import streamlit as st

from agents.intent import DEFAULT_CLASSIFIER_TEMPLATE
from config.defaults import (
    AVAILABLE_MODELS,
    DEFAULT_CORRECT_ANSWER_PROB,
    DEFAULT_INTENT_WEIGHTS,
    DEFAULT_STUDENT_PROMPTS,
    DEFAULT_TEACHER_PROMPT,
    INTENTS,
    REASONING_EFFORTS,
    STUDENT_TYPES,
    TEACHER_GREETING,
    THINKING_LEVELS,
)
from config.scenarios import TASK_SCENARIOS, TOPIC_SCENARIOS
from config.settings import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    MAX_MAX_TOKENS,
    MAX_TEMPERATURE,
    MIN_MAX_TOKENS,
    MIN_TEMPERATURE,
)

MODEL_NAMES = list(AVAILABLE_MODELS.keys())

INTENT_HELP = {
    "chat": 'Школьник пришел просто поболтать не по теме задачи или пишет мусор. Пример: "Как тебя зовут?", "ываыва", "❗😊💥", ".", "Как купить собаку".',
    "set-problem": 'Задача, которую принес школьник. Это может быть пример или тема, которую он хочет разобрать. Пример: "2x + 8 = 19", "Квадратные уравнения".',
    "answer": 'Ответ школьника на вопрос тьютора по задаче или теме, это может быть ответ на ключевой вопрос или на вспомогательный, на вопрос об общих знаниях по предмету. Ответ может быть правильным, неправильным (пример: "45", "является", "убывающая") и неопределенным ("не знаю", "черт его знает", "не понял").',
    "get-explanation": 'Школьник просит объяснить или задает вопрос по задаче, по решению в целом или по отдельным шагам. Пример: "Помоги", "как решить?", "а как?"',
    "thank-tutor": 'Школьник благодарит тьютора. Пример: "Спасибо!"',
    "agree-with-tutor": 'Школьник соглашается с тьютором, в частности, когда тьютор предлагает план действий, а школьник отвечает "да". Пример: "хорошо", "да", "давай", "погнали".',
    "find-mistake": 'Школьник просит найти ошибку в его вычислениях или решении по текущей задаче. Пример: "что здесь неверно?", "где у меня ошибка?", "почему у меня не так?".',
    "criticize-tutor": 'Школьник ругает или критикует тьютора, иногда может быть использована неприличная брань, иногда это просто указание на ошибку. Пример: "неправда, проверь еще раз", "тут ошибка".',
    "end-dialog": 'Школьник хочет завершить диалог раньше времени, прямо или косвенно обозначая это. Пример: "Я устал", "мама позвала кушать продолжим позже", "давай это в следующий раз".',
    "get-solution": 'Школьник просит тьютора дать ответ на его же вопрос или на всю задачу целиком. Пример: "реши ты", "скажи сам", "какой ответ", "сколько получится?".',
}


@st.dialog("Редактирование промпта", width="large")
def _edit_prompt(state_key, sub_key, default_value, label):
    """Full-screen modal editor for any prompt."""
    current = (
        st.session_state[state_key][sub_key]
        if sub_key
        else st.session_state[state_key]
    )
    new_val = st.text_area(label, value=current, height=400)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Сохранить", use_container_width=True):
            if sub_key:
                st.session_state[state_key][sub_key] = new_val
            else:
                st.session_state[state_key] = new_val
            st.rerun()
    with col2:
        if st.button("Сбросить к дефолтам", use_container_width=True):
            if sub_key:
                st.session_state[state_key][sub_key] = default_value
            else:
                st.session_state[state_key] = default_value
            st.rerun()


def _clamp_weight(changed_id: str):
    """Prevent total intent weights from exceeding 100."""
    weights = st.session_state.intent_weights
    for intent in INTENTS:
        wkey = f"weight_{intent['id']}"
        if wkey in st.session_state:
            weights[intent["id"]] = st.session_state[wkey]
    total = sum(weights.values())
    if total > 100:
        clamped = weights[changed_id] - (total - 100)
        st.session_state[f"weight_{changed_id}"] = max(clamped, 0)
        weights[changed_id] = st.session_state[f"weight_{changed_id}"]


def _reset_intents():
    """Callback: reset intent weights and prompts to current student type defaults."""
    stype = st.session_state.student_type
    new_weights = copy.deepcopy(DEFAULT_INTENT_WEIGHTS[stype])
    st.session_state.intent_weights = new_weights
    for iid, val in new_weights.items():
        st.session_state[f"weight_{iid}"] = val
    for intent in INTENTS:
        st.session_state.intent_prompts[intent["id"]] = intent["prompt"]


def _on_student_type_change():
    """Callback: update student prompt, intent weights, and correct answer prob when type changes."""
    student_type = st.session_state.radio_student_type
    st.session_state.student_type = student_type
    st.session_state.student_prompt = DEFAULT_STUDENT_PROMPTS[student_type]
    new_weights = copy.deepcopy(DEFAULT_INTENT_WEIGHTS[student_type])
    st.session_state.intent_weights = new_weights
    for iid, val in new_weights.items():
        st.session_state[f"weight_{iid}"] = val
    st.session_state.correct_answer_prob = DEFAULT_CORRECT_ANSWER_PROB[student_type]
    st.session_state.slider_correct_prob = DEFAULT_CORRECT_ANSWER_PROB[student_type]


def _model_options(prefix: str, default_model_key: str = "teacher_model"):
    """Render model selectbox + thinking/reasoning dropdown."""
    model_name = st.selectbox(
        "Модель",
        MODEL_NAMES,
        index=MODEL_NAMES.index(st.session_state[f"{prefix}_model"]),
        key=f"{prefix}_model_select",
    )
    st.session_state[f"{prefix}_model"] = model_name
    model_cfg = AVAILABLE_MODELS[model_name]

    if model_cfg["supports_thinking"]:
        labels = ["Нет" if v is None else v for v in THINKING_LEVELS]
        current = st.session_state.get(f"{prefix}_thinking_level")
        idx = THINKING_LEVELS.index(current) if current in THINKING_LEVELS else 0
        chosen = st.selectbox("Thinking level", labels, index=idx, key=f"{prefix}_think_sel")
        st.session_state[f"{prefix}_thinking_level"] = None if chosen == "Нет" else chosen
    else:
        st.session_state[f"{prefix}_thinking_level"] = None

    if model_cfg["supports_reasoning"]:
        labels = ["Нет" if v is None else v for v in REASONING_EFFORTS]
        current = st.session_state.get(f"{prefix}_reasoning_effort")
        idx = REASONING_EFFORTS.index(current) if current in REASONING_EFFORTS else 0
        chosen = st.selectbox("Reasoning effort", labels, index=idx, key=f"{prefix}_reason_sel")
        st.session_state[f"{prefix}_reasoning_effort"] = None if chosen == "Нет" else chosen
    else:
        st.session_state[f"{prefix}_reasoning_effort"] = None


SCENARIO_CATEGORIES = ["Свой ввод", "Задача", "Тема"]


def _scenario_label(text: str, num: int) -> str:
    """Truncated label for the scenario selectbox."""
    preview = text.replace("\n", " ")
    if len(preview) > 90:
        preview = preview[:90] + "..."
    return f"{num}. {preview}"


def render_sidebar():
    with st.sidebar:
        # ── Player controls ────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            start = st.button("▶️", key="btn_start", disabled=st.session_state.running, use_container_width=True, help="Запустить")
        with c2:
            stop = st.button("⏸️", key="btn_stop", disabled=not st.session_state.running, use_container_width=True, help="Остановить")
        with c3:
            step = st.button("⏭️", key="btn_step", disabled=st.session_state.running, use_container_width=True, help="Один шаг")
        with c4:
            clear = st.button("📝", key="btn_clear", use_container_width=True, help="Новый диалог")
        with c5:
            reset = st.button("🔄", key="btn_reset", use_container_width=True, help="Сброс всего")

        # ── Export ──────────────────────────────────────────
        if len(st.session_state.messages) > 1:
            from ui.controls import export_dialog
            st.download_button(
                "\U0001f4e5 Экспорт JSON",
                data=export_dialog(),
                file_name="dialog.json",
                mime="application/json",
                key="btn_export",
                use_container_width=True,
            )

        # ── Scenario selector ──────────────────────────────
        if len(st.session_state.messages) <= 1:
            with st.expander("Первая реплика ученика", expanded=True):
                cat = st.radio(
                    "Категория",
                    SCENARIO_CATEGORIES,
                    horizontal=True,
                    key="scenario_cat",
                    label_visibility="collapsed",
                )
                if cat == "Задача":
                    st.selectbox(
                        "Выберите задачу",
                        range(len(TASK_SCENARIOS)),
                        format_func=lambda i: _scenario_label(TASK_SCENARIOS[i], i + 1),
                        key="task_select",
                    )
                elif cat == "Тема":
                    st.selectbox(
                        "Выберите тему",
                        range(len(TOPIC_SCENARIOS)),
                        format_func=lambda i: _scenario_label(TOPIC_SCENARIOS[i], i + 1),
                        key="topic_select",
                    )
                else:
                    st.text_input(
                        "Введите задачу или тему",
                        key="custom_input",
                        placeholder="Например: Реши уравнение 2x + 5 = 13",
                    )

        # ── Teacher ─────────────────────────────────────────
        with st.expander("Репетитор", expanded=False):
            _model_options("teacher")
            st.toggle(
                "Показывать рассуждения",
                value=st.session_state.teacher_show_reasoning,
                key="toggle_teacher_reasoning",
            )
            st.session_state.teacher_show_reasoning = st.session_state.toggle_teacher_reasoning
            if st.button("Редактировать промпт", key="btn_edit_teacher"):
                _edit_prompt(
                    "teacher_prompt",
                    None,
                    DEFAULT_TEACHER_PROMPT,
                    "Промпт репетитора",
                )

        # ── Student ─────────────────────────────────────────
        with st.expander("Ученик", expanded=False):
            st.radio(
                "Тип ученика",
                STUDENT_TYPES,
                index=STUDENT_TYPES.index(st.session_state.student_type),
                key="radio_student_type",
                horizontal=True,
                on_change=_on_student_type_change,
            )

            st.session_state.correct_answer_prob = st.slider(
                "Вероятность правильного ответа, %",
                min_value=0,
                max_value=100,
                value=st.session_state.correct_answer_prob,
                step=5,
                key="slider_correct_prob",
            )

            _model_options("student")
            st.toggle(
                "Показывать рассуждения",
                value=st.session_state.student_show_reasoning,
                key="toggle_student_reasoning",
            )
            st.session_state.student_show_reasoning = st.session_state.toggle_student_reasoning
            if st.button("Редактировать промпт", key="btn_edit_student"):
                _edit_prompt(
                    "student_prompt",
                    None,
                    DEFAULT_STUDENT_PROMPTS[st.session_state.student_type],
                    "Промпт ученика",
                )

        # ── Intents ─────────────────────────────────────────
        with st.expander("Интенты", expanded=False):
            # Intent selection mode
            INTENT_MODES = ["random", "llm"]
            INTENT_MODE_LABELS = {
                "random": "Случайный (по весам)",
                "llm": "LLM-классификатор",
            }
            mode_idx = INTENT_MODES.index(st.session_state.intent_mode)
            chosen_mode = st.radio(
                "Способ выбора интента",
                INTENT_MODES,
                index=mode_idx,
                format_func=lambda m: INTENT_MODE_LABELS[m],
                horizontal=True,
                key="radio_intent_mode",
            )
            st.session_state.intent_mode = chosen_mode

            if chosen_mode == "random":
                st.caption("Интент выбирается случайно по весам ниже.")
            else:
                st.caption(
                    "LLM анализирует контекст диалога и выбирает подходящий интент. "
                    "Веса используются как ориентир распределения."
                )
                if st.button("✏️ Промпт классификатора", key="btn_edit_classifier"):
                    _edit_prompt(
                        "classifier_prompt",
                        None,
                        DEFAULT_CLASSIFIER_TEMPLATE,
                        "Промпт классификатора интентов",
                    )

            weights = st.session_state.intent_weights
            prompts = st.session_state.intent_prompts

            # Sync dict from widget keys
            for intent in INTENTS:
                wkey = f"weight_{intent['id']}"
                if wkey in st.session_state:
                    weights[intent["id"]] = st.session_state[wkey]

            remaining = 100 - sum(weights.values())

            profile_name = "Настраиваемый"
            for name, preset in DEFAULT_INTENT_WEIGHTS.items():
                if weights == preset:
                    profile_name = name
                    break
            is_custom = profile_name == "Настраиваемый"

            st.caption(f"Профиль: {profile_name} | Очков: {remaining}")

            for intent in INTENTS:
                iid = intent["id"]
                current = weights.get(iid, 0)
                col1, col2 = st.columns([5, 1])
                with col1:
                    weights[iid] = st.slider(
                        f"{intent['name']} ({iid})",
                        min_value=0,
                        max_value=100,
                        value=current,
                        key=f"weight_{iid}",
                        on_change=_clamp_weight,
                        args=(iid,),
                        help=INTENT_HELP.get(iid),
                    )
                with col2:
                    st.markdown("")
                    st.markdown("")
                    if st.button("✏️", key=f"btn_edit_{iid}"):
                        _edit_prompt(
                            "intent_prompts",
                            iid,
                            intent["prompt"],
                            f"Промпт: {intent['name']}",
                        )

            if is_custom:
                st.button(
                    "Сбросить к дефолтам",
                    key="btn_reset_intents",
                    on_click=_reset_intents,
                )

        # ── Generation params ───────────────────────────────
        with st.expander("Параметры генерации", expanded=False):
            st.session_state.temperature = st.slider(
                "Temperature",
                min_value=MIN_TEMPERATURE,
                max_value=MAX_TEMPERATURE,
                value=st.session_state.temperature,
                step=0.1,
                key="slider_temp",
            )
            st.session_state.max_tokens = st.slider(
                "Max tokens",
                min_value=MIN_MAX_TOKENS,
                max_value=MAX_MAX_TOKENS,
                value=st.session_state.max_tokens,
                step=64,
                key="slider_tokens",
            )

        # ── Handle button clicks (AFTER all widgets rendered) ──
        if clear:
            st.session_state.messages = [
                {"agent": "teacher", "content": TEACHER_GREETING, "intent_id": None}
            ]
            st.session_state.step_count = 0
            st.session_state.running = False
            st.session_state.one_step_pending = False
            st.rerun()

        if reset:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        if stop:
            st.session_state.running = False
            st.rerun()

        if step:
            from ui.controls import validate_config
            if validate_config():
                st.session_state.one_step_pending = True
                st.rerun()

        if start:
            from ui.controls import validate_config
            if validate_config():
                st.session_state.running = True
                st.rerun()
