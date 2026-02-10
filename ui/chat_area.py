"""Chat display area."""

import streamlit as st

from config.settings import STUDENT_AVATAR, TEACHER_AVATAR


def render_chat():
    """Render the conversation messages."""
    for msg in st.session_state.messages:
        if msg["agent"] == "teacher":
            with st.chat_message("assistant", avatar=TEACHER_AVATAR):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar=STUDENT_AVATAR):
                if msg.get("intent_id"):
                    st.caption(f"Намерение: **{msg['intent_id']}**")
                st.markdown(msg["content"])

    if st.session_state.messages:
        st.caption(f"Шагов: {st.session_state.step_count}")
