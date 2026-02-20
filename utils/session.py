"""Session state initialization for Streamlit."""

import copy
import os

import streamlit as st
from dotenv import load_dotenv

from agents.intent import DEFAULT_CLASSIFIER_TEMPLATE
from config.defaults import (
    DEFAULT_CORRECT_ANSWER_PROB,
    DEFAULT_INTENT_WEIGHTS,
    DEFAULT_MISTAKE_WEIGHTS,
    DEFAULT_SITUATION_WEIGHTS,
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
        "teacher_model": "Gemini 3 Flash",
        "teacher_thinking_level": "high",
        "teacher_reasoning_effort": None,
        "teacher_prompt": DEFAULT_TEACHER_PROMPT,
        "teacher_show_reasoning": True,
        # Student settings
        "student_type": "Слабый",
        "student_model": "GPT OSS 120B (Yandex)",
        "student_thinking_level": None,
        "student_reasoning_effort": "medium",
        "student_prompt": DEFAULT_STUDENT_PROMPTS["Слабый"],
        "student_show_reasoning": True,
        # Intent weights and prompts
        "intent_weights": copy.deepcopy(DEFAULT_INTENT_WEIGHTS["Слабый"]),
        "intent_prompts": {i["id"]: i["prompt"] for i in INTENTS},
        "correct_answer_prob": DEFAULT_CORRECT_ANSWER_PROB["Слабый"],
        "mistake_weights": copy.deepcopy(DEFAULT_MISTAKE_WEIGHTS["Слабый"]),
        "intent_mode": "llm",  # "random" or "llm"
        "classifier_prompt": DEFAULT_CLASSIFIER_TEMPLATE,
        "situation_weights": copy.deepcopy(DEFAULT_SITUATION_WEIGHTS["Слабый"]),
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
