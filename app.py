import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone

st.set_page_config(
    page_title="Ballers League Treasure Hunt",
    page_icon="🏆",
    layout="centered"
)
st.write("Choose your clue route according to the designated team. Remember - the first to solve these clues will get a hidden reward!! Fastest hunter wins!!")

st.write("1. Solve the Clue!")
st.write("2. Search out the mystery place according to the clue.")
st.write("3. Find the four digit code that unlocks your next clue.")
st.write("4. Enter the code and unlock your next clue!")
st.write("5. Solve all 5 clues before the other teams do! Only first THREE TEAMS WIN!")
st.write("Good Luck HUNTING the extra points!!!")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def get_all_teams():
    res = (
        supabase.table("th_teams")
        .select("team_name")
        .order("team_name")
        .execute()
    )
    return [row["team_name"] for row in (res.data or [])]


def get_team_state(team_name: str):
    res = (
        supabase.table("th_teams")
        .select("*")
        .eq("team_name", team_name)
        .single()
        .execute()
    )
    return res.data


def get_clue_for_team(team_name: str, tier: int):
    res = (
        supabase.table("th_clues")
        .select("id, team_name, tier, clue_title, clue_text, pin_code, is_final")
        .eq("team_name", team_name)
        .eq("tier", tier)
        .single()
        .execute()
    )
    return res.data


def log_attempt(team_name: str, tier: int, entered_pin: str, is_success: bool):
    supabase.table("th_attempts").insert({
        "team_name": team_name,
        "tier": tier,
        "entered_pin": entered_pin,
        "is_success": is_success
    }).execute()


def team_has_next_tier(team_name: str, next_tier: int) -> bool:
    res = (
        supabase.table("th_clues")
        .select("id")
        .eq("team_name", team_name)
        .eq("tier", next_tier)
        .limit(1)
        .execute()
    )
    return bool(res.data)


def advance_team(team_name: str, current_tier: int):
    next_tier = current_tier + 1
    has_next = team_has_next_tier(team_name, next_tier)

    if has_next:
        supabase.table("th_teams").update({
            "current_tier": next_tier,
            "is_finished": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("team_name", team_name).execute()
    else:
        supabase.table("th_teams").update({
            "current_tier": current_tier,
            "is_finished": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("team_name", team_name).execute()


def verify_pin(team_name: str, tier: int, entered_pin: str):
    clue = get_clue_for_team(team_name, tier)
    if not clue:
        return False, "No clue found for this team and tier."

    correct = str(clue["pin_code"]).strip() == entered_pin.strip()
    log_attempt(team_name, tier, entered_pin.strip(), correct)

    if correct:
        advance_team(team_name, tier)
        return True, "Correct pin."
    return False, "Wrong pin."


def reset_local_messages():
    for key in ["success_msg", "error_msg"]:
        if key in st.session_state:
            del st.session_state[key]


if "selected_team" not in st.session_state:
    st.session_state.selected_team = None

if "show_clue" not in st.session_state:
    st.session_state.show_clue = False

st.title("🏆 Ballers League Treasure Hunt")
st.caption("Select your team first. Then your clue will be revealed.")

teams = get_all_teams()

if not teams:
    st.error("No teams found in th_teams. Seed the teams table first.")
    st.stop()

if not st.session_state.show_clue:
    chosen_team = st.selectbox("Select your team", teams)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Continue"):
            st.session_state.selected_team = chosen_team
            st.session_state.show_clue = True
            st.rerun()

    with col2:
        if st.button("Reset Selection"):
            st.session_state.selected_team = None
            st.session_state.show_clue = False
            reset_local_messages()
            st.rerun()

    st.stop()

selected_team = st.session_state.selected_team

team_state = get_team_state(selected_team)
if not team_state:
    st.error("Team state not found.")
    st.stop()

current_tier = int(team_state["current_tier"])
is_finished = bool(team_state["is_finished"])

col1, col2 = st.columns([3, 1])
with col1:
    st.info(f"Team: {selected_team}")
with col2:
    if st.button("Change Team"):
        st.session_state.selected_team = None
        st.session_state.show_clue = False
        reset_local_messages()
        st.rerun()

if is_finished:
    st.success(f"{selected_team} has completed the treasure hunt.")
    st.stop()

clue = get_clue_for_team(selected_team, current_tier)
if not clue:
    st.error(f"No clue assigned for {selected_team} at tier {current_tier}.")
    st.stop()

st.subheader(clue["clue_title"])
st.write(clue["clue_text"])

with st.form("pin_form", clear_on_submit=True):
    entered_pin = st.text_input("Enter 4-digit pin", max_chars=4, type="password")
    submitted = st.form_submit_button("Unlock Next Clue")

    if submitted:
        reset_local_messages()

        if not entered_pin.strip():
            st.session_state["error_msg"] = "Please enter the pin."
        else:
            ok, message = verify_pin(selected_team, current_tier, entered_pin)
            if ok:
                st.session_state["success_msg"] = message
            else:
                st.session_state["error_msg"] = message

if "success_msg" in st.session_state:
    st.success(st.session_state["success_msg"])
    st.rerun()

if "error_msg" in st.session_state:
    st.error(st.session_state["error_msg"])
