"""LearnLM — Симулятор урока: AI Teacher-Student Chat."""

import streamlit as st

from config.settings import APP_TITLE
from ui.chat_area import render_chat
from ui.controls import execute_turn
from ui.sidebar import render_sidebar
from utils.session import init_session_state

st.set_page_config(page_title=APP_TITLE, layout="wide")

init_session_state()

st.title(APP_TITLE)

render_sidebar()
render_chat()
execute_turn()
