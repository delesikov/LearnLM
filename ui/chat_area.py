"""Chat display area with Telegram-style bubble styling."""

import streamlit as st

from config.settings import STUDENT_AVATAR, TEACHER_AVATAR

CHAT_CSS = """
<style>
/* ── Telegram-style chat bubbles ─────────────────────────── */

/* Shared bubble base */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    padding: 8px 14px !important;
    max-width: 85%;
    margin-bottom: 4px !important;
    gap: 8px !important;
}

/* Teacher (assistant) — left, light bubble */
[data-testid="stChatMessage"]:has(.chat-teacher) {
    background: rgba(128, 128, 128, 0.10) !important;
    border-radius: 4px 16px 16px 16px !important;
    margin-right: auto;
}

/* Student (user) — right, colored bubble, flipped layout */
[data-testid="stChatMessage"]:has(.chat-student) {
    background: rgba(42, 120, 240, 0.12) !important;
    border-radius: 16px 4px 16px 16px !important;
    margin-left: auto;
    flex-direction: row-reverse !important;
}

/* Compact avatar */
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarIcon"],
[data-testid="stChatMessage"] .stChatMessageAvatarIcon {
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    font-size: 18px !important;
}

/* Intent caption inside bubble */
[data-testid="stChatMessage"]:has(.chat-student) [data-testid="stCaptionContainer"] {
    text-align: right;
    opacity: 0.65;
}

/* Step counter */
.step-counter {
    text-align: center;
    opacity: 0.5;
    font-size: 0.8em;
    margin-top: 4px;
}

/* Hide marker divs */
.chat-teacher, .chat-student {
    display: none;
}
</style>
"""


def render_chat():
    """Render the conversation messages with Telegram-style bubbles."""
    st.markdown(CHAT_CSS, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["agent"] == "teacher":
            with st.chat_message("assistant", avatar=TEACHER_AVATAR):
                st.markdown('<div class="chat-teacher"></div>', unsafe_allow_html=True)
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar=STUDENT_AVATAR):
                st.markdown('<div class="chat-student"></div>', unsafe_allow_html=True)
                if msg.get("intent_id"):
                    st.caption(f"Намерение: **{msg['intent_id']}**")
                st.markdown(msg["content"])

    if st.session_state.messages:
        st.caption(f"Шагов: {st.session_state.step_count}")
