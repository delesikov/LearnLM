"""Google Sheets export: one row per dialog, one sheet per day."""

import json
import logging
import uuid
from datetime import datetime

import streamlit as st

log = logging.getLogger(__name__)

# Column headers for the sheet
HEADERS = [
    "id",
    "datetime",
    "teacher_model",
    "teacher_thinking_level",
    "student_model",
    "student_type",
    "student_thinking_level",
    "student_reasoning_effort",
    "intent_mode",
    "temperature",
    "max_tokens",
    "correct_answer_prob",
    "intent_weights",
    "step_count",
    "num_messages",
    "dialog",
    "reasoning",
]


def _get_client():
    """Create gspread client from Streamlit secrets."""
    try:
        creds = dict(st.secrets["gsheets"]["credentials"])
        spreadsheet_id = st.secrets["gsheets"]["spreadsheet_id"]
    except (KeyError, FileNotFoundError):
        return None, None

    import gspread

    client = gspread.service_account_from_dict(creds)
    spreadsheet = client.open_by_key(spreadsheet_id)
    return client, spreadsheet


def _get_or_create_sheet(spreadsheet, sheet_name: str):
    """Get existing sheet by name or create a new one with headers."""
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except Exception:
        worksheet = spreadsheet.add_worksheet(
            title=sheet_name, rows=1000, cols=len(HEADERS)
        )
        worksheet.append_row(HEADERS)
    return worksheet


def export_to_sheets() -> bool:
    """Export current dialog as one row to Google Sheets. Returns True on success."""
    _, spreadsheet = _get_client()
    if spreadsheet is None:
        st.error("Google Sheets не настроен. Проверьте секреты.")
        return False

    now = datetime.now()
    sheet_name = now.strftime("%Y-%m-%d")
    worksheet = _get_or_create_sheet(spreadsheet, sheet_name)

    # Collect reasoning from all messages into a separate JSON
    messages = st.session_state.get("messages", [])
    reasoning_list = []
    for msg in messages:
        r = msg.get("reasoning")
        if r:
            reasoning_list.append({
                "agent": msg.get("agent"),
                "reasoning": r,
            })

    # Strip reasoning from dialog JSON to keep it cleaner
    dialog_clean = []
    for msg in messages:
        dialog_clean.append({
            "agent": msg.get("agent"),
            "content": msg.get("content", ""),
            "intent_id": msg.get("intent_id"),
        })

    row = [
        str(uuid.uuid4())[:8],
        now.strftime("%Y-%m-%d %H:%M:%S"),
        st.session_state.get("teacher_model", ""),
        st.session_state.get("teacher_thinking_level", "") or "",
        st.session_state.get("student_model", ""),
        st.session_state.get("student_type", ""),
        st.session_state.get("student_thinking_level", "") or "",
        st.session_state.get("student_reasoning_effort", "") or "",
        st.session_state.get("intent_mode", ""),
        st.session_state.get("temperature", ""),
        st.session_state.get("max_tokens", ""),
        st.session_state.get("correct_answer_prob", ""),
        json.dumps(
            st.session_state.get("intent_weights", {}), ensure_ascii=False
        ),
        st.session_state.get("step_count", 0),
        len(messages),
        json.dumps(dialog_clean, ensure_ascii=False),
        json.dumps(reasoning_list, ensure_ascii=False) if reasoning_list else "",
    ]

    try:
        worksheet.append_row(row, value_input_option="RAW")
        log.info("Dialog exported to sheet %s", sheet_name)
        return True
    except Exception as e:
        log.error("Failed to export to Google Sheets: %s", e)
        st.error(f"Ошибка записи в Google Sheets: {e}")
        return False
