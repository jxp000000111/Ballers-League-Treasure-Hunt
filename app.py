import random
from typing import Dict, List, Optional, Tuple

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Treasure Hunt", page_icon="🗝️", layout="centered")

# =================================================
# CONFIGURATION
# =================================================
# This version is deployment-ready for Streamlit Community Cloud.
# It uses Google Sheets as the backend so data persists for all users.
#
# SHEETS REQUIRED:
# 1. users
# 2. clue_1_pool
# 3. clue_2_pool
# 4. clue_3_pool
#
# users sheet columns:
# username, clue_1, clue_2, clue_3, unlocked_clue_1, unlocked_clue_2,
# unlocked_clue_3, unlocked_final_clue, eliminated
#
# clue pool sheet columns:
# clue_text, assigned_to
# =================================================

APP_TITLE = "🗝️ Treasure Hunt App"
FINAL_CLUE_TEXT = "Final clue: The treasure rests where every match begins, but never stays for long."

PINS = {
    "clue_2": "4821",
    "clue_3": "7354",
    "final_clue": "9167",
}

USERS_SHEET = "users"
POOL_SHEETS = {
    "clue_1": "clue_1_pool",
    "clue_2": "clue_2_pool",
    "clue_3": "clue_3_pool",
}

USERS_HEADERS = [
    "username",
    "clue_1",
    "clue_2",
    "clue_3",
    "unlocked_clue_1",
    "unlocked_clue_2",
    "unlocked_clue_3",
    "unlocked_final_clue",
    "eliminated",
]

POOL_HEADERS = ["clue_text", "assigned_to"]


# =================================================
# GOOGLE SHEETS CONNECTION
# =================================================
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials_info = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"],
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
    }

    creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    return gspread.authorize(creds)


@st.cache_resource
def get_spreadsheet():
    client = get_gspread_client()
    spreadsheet_name = st.secrets["app"]["spreadsheet_name"]
    return client.open(spreadsheet_name)


def get_worksheet(sheet_name: str):
    return get_spreadsheet().worksheet(sheet_name)


# =================================================
# SHEET INITIALIZATION
# =================================================
def ensure_sheet_headers(sheet_name: str, headers: List[str]):
    ws = get_worksheet(sheet_name)
    first_row = ws.row_values(1)
    if first_row != headers:
        ws.clear()
        ws.append_row(headers)


def initialize_sheets():
    ensure_sheet_headers(USERS_SHEET, USERS_HEADERS)
    for pool_sheet in POOL_SHEETS.values():
        ensure_sheet_headers(pool_sheet, POOL_HEADERS)


# =================================================
# DATA HELPERS
# =================================================
def str_to_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def bool_to_str(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def get_all_users() -> List[Dict[str, str]]:
    ws = get_worksheet(USERS_SHEET)
    return ws.get_all_records()


def find_user_row(username: str) -> Tuple[Optional[int], Optional[Dict[str, str]]]:
    ws = get_worksheet(USERS_SHEET)
    records = ws.get_all_records()
    for index, row in enumerate(records, start=2):
        if str(row.get("username", "")).strip().lower() == username.strip().lower():
            return index, row
    return None, None


def create_user_if_needed(username: str):
    row_index, _ = find_user_row(username)
    if row_index is not None:
        return

    ws = get_worksheet(USERS_SHEET)
    ws.append_row(
        [
            username,
            "",
            "",
            "",
            "FALSE",
            "FALSE",
            "FALSE",
            "FALSE",
            "FALSE",
        ]
    )


def update_user_field(username: str, column_name: str, value: str):
    ws = get_worksheet(USERS_SHEET)
    row_index, _ = find_user_row(username)
    if row_index is None:
        return

    column_index = USERS_HEADERS.index(column_name) + 1
    ws.update_cell(row_index, column_index, value)


def get_user(username: str) -> Optional[Dict[str, str]]:
    _, row = find_user_row(username)
    return row


def set_unlocked(username: str, clue_key: str):
    column_map = {
        "clue_1": "unlocked_clue_1",
        "clue_2": "unlocked_clue_2",
        "clue_3": "unlocked_clue_3",
        "final_clue": "unlocked_final_clue",
    }
    update_user_field(username, column_map[clue_key], "TRUE")


def set_eliminated(username: str, eliminated: bool = True):
    update_user_field(username, "eliminated", bool_to_str(eliminated))


# =================================================
# CLUE POOL HELPERS
# =================================================
def get_pool_records(clue_key: str) -> List[Dict[str, str]]:
    ws = get_worksheet(POOL_SHEETS[clue_key])
    return ws.get_all_records()


def assign_unique_clue(username: str, clue_key: str) -> Optional[str]:
    ws = get_worksheet(POOL_SHEETS[clue_key])
    records = ws.get_all_records()

    available_rows = []
    for idx, row in enumerate(records, start=2):
        assigned_to = str(row.get("assigned_to", "")).strip()
        clue_text = str(row.get("clue_text", "")).strip()
        if clue_text and not assigned_to:
            available_rows.append((idx, clue_text))

    if not available_rows:
        return None

    chosen_row, chosen_clue = random.choice(available_rows)
    ws.update_cell(chosen_row, 2, username)
    update_user_field(username, clue_key, chosen_clue)
    return chosen_clue


# =================================================
# APP LOGIC
# =================================================
def verify_pin(clue_key: str, entered_pin: str) -> bool:
    return entered_pin == PINS[clue_key]


def select_clue(clue_key: str):
    st.session_state.selected_clue = clue_key


def show_login():
    st.subheader("Enter your team name")
    username = st.text_input("Team Name", placeholder="Example: Eagles FC")

    if st.button("Start Hunt", use_container_width=True):
        cleaned = username.strip()
        if not cleaned:
            st.error("Please enter a valid team name.")
            return

        create_user_if_needed(cleaned)

        # Every team gets Clue 1 immediately. There are 7 rows available in clue_1_pool.
        user = get_user(cleaned)
        existing_clue_1 = str(user.get("clue_1", "")).strip() if user else ""
        if not existing_clue_1:
            assigned = assign_unique_clue(cleaned, "clue_1")
            if not assigned:
                set_eliminated(cleaned, True)
                st.error("No Clue 1 is available. This team joined too late.")
                return

        st.session_state.active_user = cleaned
        st.success(f"Welcome, {cleaned}!")


def show_clue_buttons():
    st.subheader("Choose a clue")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clue 1", use_container_width=True):
            select_clue("clue_1")
    with col2:
        if st.button("Clue 2", use_container_width=True):
            select_clue("clue_2")

    col3, col4 = st.columns(2)
    with col3:
        if st.button("Clue 3", use_container_width=True):
            select_clue("clue_3")
    with col4:
        if st.button("Final Clue", use_container_width=True):
            select_clue("final_clue")


def show_selected_clue():
    username = st.session_state.get("active_user", "")
    clue_key = st.session_state.get("selected_clue")

    if not username or not clue_key:
        return

    user = get_user(username)
    if not user:
        st.error("User record not found.")
        return

    eliminated = str_to_bool(user.get("eliminated", "FALSE"))
    clue_1_text = str(user.get("clue_1", "")).strip()
    clue_2_text = str(user.get("clue_2", "")).strip()
    clue_3_text = str(user.get("clue_3", "")).strip()

    unlocked_1 = str_to_bool(user.get("unlocked_clue_1", "FALSE"))
    unlocked_2 = str_to_bool(user.get("unlocked_clue_2", "FALSE"))
    unlocked_3 = str_to_bool(user.get("unlocked_clue_3", "FALSE"))
    unlocked_final = str_to_bool(user.get("unlocked_final_clue", "FALSE"))

    title_map = {
        "clue_1": "Clue 1",
        "clue_2": "Clue 2",
        "clue_3": "Clue 3",
        "final_clue": "Final Clue",
    }

    st.markdown("---")
    st.subheader(title_map[clue_key])

    if eliminated:
        st.error("This team has been eliminated.")
        return

    if clue_key == "clue_2" and not unlocked_1:
        st.warning("You must unlock Clue 1 first.")
        return
    if clue_key == "clue_3" and not unlocked_2:
        st.warning("You must unlock Clue 2 first.")
        return
    if clue_key == "final_clue" and not unlocked_3:
        st.warning("You must unlock Clue 3 first.")
        return

    if clue_key == "clue_1":
        set_unlocked(username, "clue_1")
        st.success("Unlocked successfully.")
        st.info(clue_1_text)
        return

    if clue_key == "clue_2" and unlocked_2:
        st.success("PIN verified.")
        st.info(clue_2_text)
        return
    if clue_key == "clue_3" and unlocked_3:
        st.success("PIN verified.")
        st.info(clue_3_text)
        return
    if clue_key == "final_clue" and unlocked_final:
        st.success("PIN verified.")
        st.info(FINAL_CLUE_TEXT)
        return

    entered_pin = st.text_input(
        "Enter the 4-digit PIN",
        max_chars=4,
        type="password",
        key=f"pin_{clue_key}",
        placeholder="Enter PIN",
    )

    if st.button("Unlock Clue", use_container_width=True):
        if not entered_pin.isdigit() or len(entered_pin) != 4:
            st.error("Please enter a valid 4-digit PIN.")
            return

        if not verify_pin(clue_key, entered_pin):
            st.error("Incorrect PIN. Try again.")
            return

        if clue_key == "clue_2" and not clue_2_text:
            clue_2_text = assign_unique_clue(username, "clue_2")
            if not clue_2_text:
                set_eliminated(username, True)
                st.error("No Clue 2 is available. This team reached too late and is eliminated.")
                return

        if clue_key == "clue_3" and not clue_3_text:
            clue_3_text = assign_unique_clue(username, "clue_3")
            if not clue_3_text:
                set_eliminated(username, True)
                st.error("No Clue 3 is available. This team reached too late and is eliminated.")
                return

        set_unlocked(username, clue_key)
        st.success("Correct PIN. Clue unlocked!")

        if clue_key == "clue_2":
            st.info(clue_2_text)
        elif clue_key == "clue_3":
            st.info(clue_3_text)
        elif clue_key == "final_clue":
            st.info(FINAL_CLUE_TEXT)


def reset_everything():
    ws = get_worksheet(USERS_SHEET)
    ws.clear()
    ws.append_row(USERS_HEADERS)

    for clue_key, sheet_name in POOL_SHEETS.items():
        pool_ws = get_worksheet(sheet_name)
        existing = pool_ws.get_all_records()
        clue_texts = [str(row.get("clue_text", "")).strip() for row in existing if str(row.get("clue_text", "")).strip()]

        pool_ws.clear()
        pool_ws.append_row(POOL_HEADERS)
        for clue_text in clue_texts:
            pool_ws.append_row([clue_text, ""])


# =================================================
# UI
# =================================================
initialize_sheets()

if "active_user" not in st.session_state:
    st.session_state.active_user = ""
if "selected_clue" not in st.session_state:
    st.session_state.selected_clue = None

st.title(APP_TITLE)
st.write(
    "This public version uses Google Sheets as the backend. Teams get unique clues for Clue 1, Clue 2, and Clue 3. The final clue is common for all who reach it."
)

with st.sidebar:
    st.header("Admin")
    st.caption("Use these controls only during testing or event setup.")

    admin_password = st.text_input("Admin password", type="password")
    if st.button("Reset all progress", use_container_width=True):
        expected_password = st.secrets["app"]["admin_password"]
        if admin_password == expected_password:
            reset_everything()
            st.session_state.active_user = ""
            st.session_state.selected_clue = None
            st.success("All progress has been reset.")
        else:
            st.error("Incorrect admin password.")

if not st.session_state.active_user:
    show_login()
else:
    st.success(f"Logged in as: {st.session_state.active_user}")
    show_clue_buttons()
    show_selected_clue()

st.markdown("---")
st.caption(
    "Expected pool sizes for your format: 7 clues in clue_1_pool, 6 in clue_2_pool, 5 in clue_3_pool, and one shared final clue inside the app."
)

# =================================================
# SETUP NOTES
# =================================================
# Create these Google Sheets tabs exactly:
# - users
# - clue_1_pool
# - clue_2_pool
# - clue_3_pool
#
# Put these clue texts into the clue pool sheets under the clue_text column.
# Leave assigned_to blank.
#
# clue_1_pool should contain 7 rows
# clue_2_pool should contain 6 rows
# clue_3_pool should contain 5 rows
#
# Streamlit secrets format:
# [app]
# spreadsheet_name = "YOUR_GOOGLE_SHEET_NAME"
# admin_password = "YOUR_ADMIN_PASSWORD"
#
# [gcp_service_account]
# type = "service_account"
# project_id = "..."
# private_key_id = "..."
# private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
# client_email = "..."
# client_id = "..."
# auth_uri = "https://accounts.google.com/o/oauth2/auth"
# token_uri = "https://oauth2.googleapis.com/token"
# auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
# client_x509_cert_url = "..."
#
# requirements.txt:
# streamlit
# gspread
# google-auth
