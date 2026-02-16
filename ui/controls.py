"""Control buttons and dialog loop logic."""

import json
import time

import streamlit as st

from agents.student import StudentAgent
from agents.teacher import TeacherAgent
from config.defaults import AVAILABLE_MODELS, INTENTS, TEACHER_GREETING
from config.scenarios import TASK_SCENARIOS, TOPIC_SCENARIOS
from config.settings import MAX_DIALOG_STEPS, STUDENT_AVATAR, TEACHER_AVATAR
from models.base import Message
from models.gemini_provider import GeminiProvider
from models.openai_compat import OpenAICompatProvider


def _stream_text(text, chunk_size=3, delay=0.015):
    """Yield text in small chunks for st.write_stream typing effect."""
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]
        time.sleep(delay)


def _create_provider(prefix: str):
    """Create LLM provider based on current session settings."""
    model_name = st.session_state[f"{prefix}_model"]
    model_cfg = AVAILABLE_MODELS[model_name]

    if model_cfg["provider"] == "gemini":
        api_key = st.session_state.gemini_api_key
        if not api_key:
            st.error("Gemini API Key не задан!")
            return None
        return GeminiProvider(
            api_key=api_key,
            model_id=model_cfg["model_id"],
            thinking_level=st.session_state.get(f"{prefix}_thinking_level"),
        )
    else:
        api_key = st.session_state.yandex_api_key
        folder_id = st.session_state.yandex_folder_id
        if not api_key or not folder_id:
            st.error("Yandex API Key и Folder ID должны быть заданы!")
            return None
        return OpenAICompatProvider(
            api_key=api_key,
            folder_id=folder_id,
            model_id=model_cfg["model_id"],
            reasoning_effort=st.session_state.get(f"{prefix}_reasoning_effort"),
        )


def _get_teacher_history() -> list[Message]:
    """Build history from teacher's perspective: teacher=assistant, student=user."""
    history = []
    for msg in st.session_state.messages:
        if msg["agent"] == "teacher":
            history.append(Message(role="assistant", content=msg["content"]))
        else:
            history.append(Message(role="user", content=msg["content"]))
    return history


def _get_student_history() -> list[Message]:
    """Build history from student's perspective: student=assistant, teacher=user (flipped)."""
    history = []
    for msg in st.session_state.messages:
        if msg["agent"] == "teacher":
            history.append(Message(role="user", content=msg["content"]))
        else:
            history.append(Message(role="assistant", content=msg["content"]))
    return history


def validate_config() -> bool:
    """Validate that intents sum to 100% and API keys are set."""
    total = sum(st.session_state.intent_weights.values())
    if total != 100:
        st.error(f"Сумма вероятностей интентов = {total}% (должна быть 100%)")
        return False

    teacher_model = AVAILABLE_MODELS[st.session_state.teacher_model]
    student_model = AVAILABLE_MODELS[st.session_state.student_model]

    if teacher_model["provider"] == "gemini" or student_model["provider"] == "gemini":
        if not st.session_state.gemini_api_key:
            st.error("Gemini API Key не задан!")
            return False

    if teacher_model["provider"] == "yandex" or student_model["provider"] == "yandex":
        if not st.session_state.yandex_api_key or not st.session_state.yandex_folder_id:
            st.error("Yandex API Key и Folder ID должны быть заданы!")
            return False

    return True


def _show_api_error(agent_name: str, error: Exception):
    """Display a user-friendly API error message."""
    error_type = type(error).__name__
    st.error(
        f"**{agent_name}: ошибка API**\n\n"
        f"`{error_type}`: {error}\n\n"
        "Попробуйте ещё раз или смените модель.",
        icon="\u26a0\ufe0f",
    )


def _stream_teacher_turn() -> bool:
    """Generate and stream one teacher message."""
    provider = _create_provider("teacher")
    if not provider:
        return False

    teacher = TeacherAgent(provider, st.session_state.teacher_prompt)

    try:
        with st.spinner("\U0001f468\u200d\U0001f3eb Репетитор думает..."):
            llm_response = teacher.generate(
                history=_get_teacher_history(),
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
            )
    except Exception as e:
        _show_api_error("Репетитор", e)
        return False

    response = llm_response.text
    reasoning = llm_response.reasoning

    # Detect [SOLVED] marker and strip it before display
    solved = "[SOLVED]" in response
    if solved:
        response = response.replace("[SOLVED]", "").strip()

    with st.chat_message("assistant", avatar=TEACHER_AVATAR):
        if reasoning and st.session_state.get("teacher_show_reasoning", True):
            with st.expander("💭 Рассуждения модели"):
                st.markdown(reasoning)
        st.write_stream(_stream_text(response))

    st.session_state.messages.append({
        "agent": "teacher",
        "content": response,
        "reasoning": reasoning,
        "intent_id": None,
    })

    # Increment step count after teacher responds to student (not initial greeting)
    if len(st.session_state.messages) > 1:
        st.session_state.step_count += 1

    if solved:
        st.session_state.running = False
        st.success("Задача решена! Сессия завершена.")

    return True


def _stream_student_turn() -> bool:
    """Generate and stream one student message with intent."""
    provider = _create_provider("student")
    if not provider:
        return False

    student = StudentAgent(provider, st.session_state.student_prompt)

    intent_mode = st.session_state.get("intent_mode", "random")
    llm_kwargs = {}
    if intent_mode == "llm":
        llm_kwargs = {
            "intent_mode": "llm",
            "intent_names": {i["id"]: i["name"] for i in INTENTS},
            "student_type": st.session_state.student_type,
            "classifier_template": st.session_state.get("classifier_prompt", ""),
        }

    try:
        with st.spinner("\U0001f392 Ученик думает..."):
            llm_response, intent_id = student.generate(
                history=_get_student_history(),
                intent_weights=st.session_state.intent_weights,
                intent_prompts=st.session_state.intent_prompts,
                temperature=st.session_state.temperature,
                max_tokens=st.session_state.max_tokens,
                correct_answer_prob=st.session_state.get("correct_answer_prob", 50),
                **llm_kwargs,
            )
    except Exception as e:
        _show_api_error("Ученик", e)
        return False

    response = llm_response.text
    reasoning = llm_response.reasoning

    with st.chat_message("user", avatar=STUDENT_AVATAR):
        st.caption(f"Намерение: **{intent_id}**")
        if reasoning and st.session_state.get("student_show_reasoning", True):
            with st.expander("💭 Рассуждения модели"):
                st.markdown(reasoning)
        st.write_stream(_stream_text(response))

    st.session_state.messages.append({
        "agent": "student",
        "content": response,
        "reasoning": reasoning,
        "intent_id": intent_id,
    })
    return True


def _get_first_student_input() -> str | None:
    """Resolve the first student input from scenario selector or custom text."""
    cat = st.session_state.get("scenario_cat", "Свой ввод")
    if cat == "Задача":
        idx = st.session_state.get("task_select", 0)
        return TASK_SCENARIOS[idx]
    elif cat == "Тема":
        idx = st.session_state.get("topic_select", 0)
        return TOPIC_SCENARIOS[idx]
    else:
        custom = st.session_state.get("custom_input", "").strip()
        return custom if custom else None


def _inject_student_input(text: str):
    """Display and record a pre-made / custom student message."""
    with st.chat_message("user", avatar=STUDENT_AVATAR):
        st.write_stream(_stream_text(text))

    st.session_state.messages.append({
        "agent": "student",
        "content": text,
        "intent_id": None,
    })


def export_dialog() -> str:
    """Export dialog as JSON string."""
    data = {
        "config": {
            "teacher_model": st.session_state.teacher_model,
            "student_type": st.session_state.student_type,
            "student_model": st.session_state.student_model,
            "temperature": st.session_state.temperature,
            "max_tokens": st.session_state.max_tokens,
            "intent_probabilities": st.session_state.intent_weights,
        },
        "messages": st.session_state.messages,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)




def execute_turn():
    """Generate and stream one message if a turn is pending."""
    should_act = st.session_state.running or st.session_state.get("one_step_pending", False)
    if not should_act:
        return

    st.session_state.one_step_pending = False

    if st.session_state.step_count >= MAX_DIALOG_STEPS:
        st.session_state.running = False
        st.warning(f"Достигнут лимит в {MAX_DIALOG_STEPS} шагов.")
        return

    messages = st.session_state.messages

    if messages[-1]["agent"] == "teacher":
        # After teacher's greeting, inject pre-selected input instead of AI student
        if len(messages) == 1:
            first_input = _get_first_student_input()
            if first_input:
                _inject_student_input(first_input)
                ok = True
            else:
                ok = _stream_student_turn()
        else:
            ok = _stream_student_turn()
    else:
        ok = _stream_teacher_turn()

    if not ok:
        st.session_state.running = False
        return

    time.sleep(0.3)
    st.rerun()
