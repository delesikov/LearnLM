"""Sidebar: API keys, model selection, prompts, intents, generation params."""

import copy

import streamlit as st

from config.defaults import (
    AVAILABLE_MODELS,
    DEFAULT_INTENT_WEIGHTS,
    DEFAULT_STUDENT_PROMPTS,
    INTENTS,
    REASONING_EFFORTS,
    STUDENT_TYPES,
    THINKING_LEVELS,
)
from config.settings import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    MAX_MAX_TOKENS,
    MAX_TEMPERATURE,
    MIN_MAX_TOKENS,
    MIN_TEMPERATURE,
)

MODEL_NAMES = list(AVAILABLE_MODELS.keys())


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


def render_sidebar():
    with st.sidebar:
        # ── Teacher ─────────────────────────────────────────
        with st.expander("Репетитор", expanded=False):
            _model_options("teacher")
            st.session_state.teacher_prompt = st.text_area(
                "Системный промпт",
                value=st.session_state.teacher_prompt,
                height=200,
                key="ta_teacher_prompt",
            )

        # ── Student ─────────────────────────────────────────
        with st.expander("Ученик", expanded=False):
            prev_type = st.session_state.student_type
            student_type = st.radio(
                "Тип ученика",
                STUDENT_TYPES,
                index=STUDENT_TYPES.index(st.session_state.student_type),
                key="radio_student_type",
                horizontal=True,
            )

            if student_type != prev_type:
                st.session_state.student_type = student_type
                st.session_state.student_prompt = DEFAULT_STUDENT_PROMPTS[student_type]
                st.session_state.intent_weights = copy.deepcopy(
                    DEFAULT_INTENT_WEIGHTS[student_type]
                )

            _model_options("student")
            st.session_state.student_prompt = st.text_area(
                "Системный промпт",
                value=st.session_state.student_prompt,
                height=200,
                key="ta_student_prompt",
            )

        # ── Intents ─────────────────────────────────────────
        with st.expander("Намерения ученика", expanded=False):
            weights = st.session_state.intent_weights
            prompts = st.session_state.intent_prompts

            for intent in INTENTS:
                iid = intent["id"]
                col1, col2 = st.columns([1, 3])
                with col1:
                    weights[iid] = st.number_input(
                        intent["name"],
                        min_value=0,
                        max_value=100,
                        value=weights.get(iid, 0),
                        step=1,
                        key=f"weight_{iid}",
                    )
                with col2:
                    prompts[iid] = st.text_area(
                        f"Промпт: {intent['name']}",
                        value=prompts.get(iid, intent["prompt"]),
                        height=80,
                        key=f"prompt_{iid}",
                        label_visibility="collapsed",
                    )

            total = sum(weights.values())
            if total == 100:
                st.success(f"Сумма: {total}%")
            else:
                st.error(f"Сумма: {total}% (должна быть 100%)")

            if st.button("Сбросить к дефолтам", key="btn_reset_intents"):
                stype = st.session_state.student_type
                st.session_state.intent_weights = copy.deepcopy(
                    DEFAULT_INTENT_WEIGHTS[stype]
                )
                for intent in INTENTS:
                    st.session_state.intent_prompts[intent["id"]] = intent["prompt"]
                st.rerun()

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
