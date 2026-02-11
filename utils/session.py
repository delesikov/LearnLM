"""Session state initialization for Streamlit."""

import copy
import os

import streamlit as st
from dotenv import load_dotenv

from config.defaults import (
    DEFAULT_CORRECT_ANSWER_PROB,
    DEFAULT_INTENT_WEIGHTS,
    DEFAULT_STUDENT_PROMPTS,
    DEFAULT_TEACHER_PROMPT,
    INTENTS,
    TEACHER_GREETING,
)
from config.settings import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE


def _get_secret(key: str, default: str = "") -> str:
    """Read secret from st.secrets (Streamlit Cloud) or env vars (local)."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)


def init_session_state():
    """Initialize all session_state keys with defaults (only if missing)."""
    load_dotenv()

    defaults = {
        # API keys (st.secrets for Cloud, .env for local)
        "gemini_api_key": _get_secret("GEMINI_API_KEY"),
        "yandex_api_key": _get_secret("YANDEX_API_KEY"),
        "yandex_folder_id": _get_secret("YANDEX_FOLDER_ID"),
        # Teacher settings
        "teacher_model": "Gemini 2.5 Flash",
        "teacher_thinking_level": None,
        "teacher_reasoning_effort": None,
        "teacher_prompt": DEFAULT_TEACHER_PROMPT,
        # Student settings
        "student_type": "Слабый",
        "student_model": "Gemini 2.5 Flash",
        "student_thinking_level": None,
        "student_reasoning_effort": None,
        "student_prompt": DEFAULT_STUDENT_PROMPTS["Слабый"],
        # Intent weights and prompts
        "intent_weights": copy.deepcopy(DEFAULT_INTENT_WEIGHTS["Слабый"]),
        "intent_prompts": {i["id"]: i["prompt"] for i in INTENTS},
        "correct_answer_prob": DEFAULT_CORRECT_ANSWER_PROB["Слабый"],
        # Generation parameters
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS,
        # Dialog state (starts with static greeting)
        "messages": [{"agent": "teacher", "content": TEACHER_GREETING, "intent_id": None}],
        "step_count": 0,
        "running": False,
        "one_step_pending": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
