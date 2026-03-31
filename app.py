import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re

st.set_page_config(
    page_title="Ballers League Treasure Hunt",
    page_icon="🏆",
    layout="centered"
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

TEAM_LOGOS = {
    "Amigos FC": "https://ballers-league.vercel.app/logos/amigos.png",
    "Men in Black FC": "https://ballers-league.vercel.app/logos/meninblack.png",
    "Timeless Titans": "https://ballers-league.vercel.app/logos/timelesstitans.png",
    "Galacticos 7": "https://ballers-league.vercel.app/logos/galacticos7.png",
    "Red Devilz": "https://ballers-league.vercel.app/logos/reddevilz.png",
    "Beast FC": "https://ballers-league.vercel.app/logos/beast.png",
    "Blue Lock FC": "https://ballers-league.vercel.app/logos/bluelock.png",
}

BALLERS_LOGO = "https://ballers-league.vercel.app/logos/ballers-league-vol2.png"


def normalize_answer(text: str) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


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


def get_all_team_states():
    res = (
        supabase.table("th_teams")
        .select("*")
        .execute()
    )
    return res.data or []


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


def get_quiz_for_team(team_name: str, tier: int):
    res = (
        supabase.table("th_quiz")
        .select("*")
        .eq("team_name", team_name)
        .eq("tier", tier)
        .single()
        .execute()
    )
    return res.data


def get_quiz_progress(team_name: str, tier: int):
    res = (
        supabase.table("th_quiz_progress")
        .select("*")
        .eq("team_name", team_name)
        .eq("tier", tier)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


def unlock_quiz_for_tier(team_name: str, tier: int):
    supabase.table("th_quiz_progress").upsert(
        {
            "team_name": team_name,
            "tier": tier,
            "is_unlocked": True,
            "is_correct": False,
            "answered_at": None
        },
        on_conflict="team_name,tier"
    ).execute()


def mark_quiz_correct(team_name: str, tier: int):
    now_ts = datetime.now(timezone.utc).isoformat()
    supabase.table("th_quiz_progress").upsert(
        {
            "team_name": team_name,
            "tier": tier,
            "is_unlocked": True,
            "is_correct": True,
            "answered_at": now_ts
        },
        on_conflict="team_name,tier"
    ).execute()


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


def get_max_tier_for_team(team_name: str) -> int:
    res = (
        supabase.table("th_clues")
        .select("tier")
        .eq("team_name", team_name)
        .order("tier", desc=True)
        .limit(1)
        .execute()
    )
    if res.data:
        return int(res.data[0]["tier"])
    return 1


def advance_team(team_name: str, current_tier: int):
    next_tier = current_tier + 1
    has_next = team_has_next_tier(team_name, next_tier)
    now_ts = datetime.now(timezone.utc).isoformat()

    if has_next:
        supabase.table("th_teams").update({
            "current_tier": next_tier,
            "is_finished": False,
            "finished_at": None,
            "updated_at": now_ts
        }).eq("team_name", team_name).execute()
    else:
        supabase.table("th_teams").update({
            "current_tier": current_tier,
            "is_finished": True,
            "finished_at": now_ts,
            "updated_at": now_ts
        }).eq("team_name", team_name).execute()


def verify_pin(team_name: str, tier: int, entered_pin: str):
    clue = get_clue_for_team(team_name, tier)
    if not clue:
        return False, "No clue found for this team and tier."

    correct = str(clue["pin_code"]).strip() == entered_pin.strip()
    log_attempt(team_name, tier, entered_pin.strip(), correct)

    if correct:
        unlock_quiz_for_tier(team_name, tier)
        return True, "Correct pin. Quiz unlocked."
    return False, "Wrong pin. Try again."


def reset_local_messages():
    for key in ["success_msg", "error_msg"]:
        if key in st.session_state:
            del st.session_state[key]


if "selected_team" not in st.session_state:
    st.session_state.selected_team = None
if "show_clue" not in st.session_state:
    st.session_state.show_clue = False
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "play"

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top, rgba(42,84,180,0.24) 0%, rgba(10,20,46,1) 24%, rgba(5,10,24,1) 62%, rgba(2,5,14,1) 100%);
        color: white;
    }

    .block-container {
        max-width: 980px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    .hero-wrap {
        text-align: center;
        margin-bottom: 1.2rem;
    }

    .hero-logo {
        width: 160px;
        margin: 0 auto 0.8rem auto;
        display: block;
        filter: drop-shadow(0 12px 24px rgba(0,0,0,0.35));
    }

    .hero-title {
        font-size: 2.55rem;
        font-weight: 900;
        letter-spacing: 1px;
        color: #ffffff;
        margin-bottom: 0.25rem;
        text-align: center;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #c8d9ff;
        text-align: center;
        margin-bottom: 1.2rem;
    }

    .premium-card {
        background: linear-gradient(180deg, rgba(18,31,66,0.96) 0%, rgba(7,14,35,0.98) 100%);
        border: 1px solid rgba(134,173,255,0.18);
        border-radius: 22px;
        padding: 1.35rem;
        box-shadow: 0 18px 44px rgba(0,0,0,0.28);
        backdrop-filter: blur(10px);
        margin-bottom: 1.2rem;
    }

    .final-card {
        background: linear-gradient(180deg, rgba(85,44,10,0.96) 0%, rgba(41,21,5,0.98) 100%);
        border: 1px solid rgba(255,198,92,0.24);
        border-radius: 24px;
        padding: 1.4rem;
        box-shadow: 0 18px 44px rgba(0,0,0,0.32);
        margin-bottom: 1.2rem;
    }

    .quiz-card {
        background: linear-gradient(180deg, rgba(31,50,96,0.96) 0%, rgba(11,20,48,0.98) 100%);
        border: 1px solid rgba(110,160,255,0.2);
        border-radius: 22px;
        padding: 1.35rem;
        box-shadow: 0 18px 44px rgba(0,0,0,0.28);
        margin-bottom: 1.2rem;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.8rem;
    }

    .muted-text {
        color: #c7d6fb;
        font-size: 0.98rem;
    }

    .rules-box ol {
        margin-top: 0.4rem;
        margin-bottom: 0.4rem;
        padding-left: 1.2rem;
    }

    .rules-box li {
        margin-bottom: 0.65rem;
        color: #e8efff;
        line-height: 1.45;
    }

    .team-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        font-weight: 700;
        margin-bottom: 0.7rem;
    }

    .clue-title {
        font-size: 1.75rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 0.8rem;
        text-align: center;
    }

    .clue-text {
        color: #eef3ff;
        font-size: 1.05rem;
        line-height: 1.75;
        white-space: pre-line;
        text-align: center;
        padding: 0.5rem 0.4rem 0.3rem 0.4rem;
    }

    .final-title {
        font-size: 1.8rem;
        font-weight: 900;
        text-align: center;
        color: #ffd36f;
        margin-bottom: 0.8rem;
    }

    .footer-note {
        text-align: center;
        color: #b9cbf7;
        margin-top: 0.6rem;
        font-size: 0.95rem;
    }

    .progress-wrap {
        margin-top: 0.3rem;
        margin-bottom: 1rem;
    }

    .progress-label {
        color: #cbd8ff;
        font-size: 0.95rem;
        margin-bottom: 0.4rem;
        text-align: center;
    }

    .progress-bar {
        width: 100%;
        height: 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #4a8fff 0%, #7aa8ff 100%);
    }

    .team-card-wrap {
        margin-bottom: 0.9rem;
    }

    .team-card {
        background: linear-gradient(180deg, rgba(24,40,83,0.96) 0%, rgba(10,19,46,0.98) 100%);
        border: 1px solid rgba(134,173,255,0.18);
        border-radius: 18px;
        padding: 1rem 0.8rem 0.85rem 0.8rem;
        text-align: center;
        min-height: 210px;
        box-shadow: 0 14px 34px rgba(0,0,0,0.22);
    }

    .team-card-selected {
        border: 1px solid rgba(255,210,102,0.65);
        box-shadow: 0 0 0 1px rgba(255,210,102,0.28), 0 16px 38px rgba(0,0,0,0.28);
    }

    .team-logo {
        width: 86px;
        height: 86px;
        object-fit: contain;
        margin: 0 auto 0.65rem auto;
        display: block;
        filter: drop-shadow(0 8px 16px rgba(0,0,0,0.25));
    }

    .team-name {
        font-weight: 800;
        color: white;
        font-size: 1rem;
        margin-bottom: 0.45rem;
        min-height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .team-tier {
        color: #c8d9ff;
        font-size: 0.92rem;
        margin-bottom: 0.25rem;
    }

    .team-finish {
        color: #ffd36f;
        font-size: 0.9rem;
        font-weight: 700;
    }

    .leader-row {
        display: grid;
        grid-template-columns: 60px 1fr 110px 120px 220px;
        gap: 12px;
        align-items: center;
        padding: 0.9rem 0.2rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }

    .leader-head {
        font-weight: 900;
        color: #aac7ff;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(255,255,255,0.12);
    }

    .rank-pill {
        width: 38px;
        height: 38px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        font-weight: 900;
        background: rgba(255,255,255,0.08);
    }

    .rank-top {
        background: linear-gradient(180deg, #f7c948 0%, #d59d10 100%);
        color: #231700;
    }

    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding-top: 0.72rem !important;
        padding-bottom: 0.72rem !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

teams = get_all_teams()
team_states = get_all_team_states()

if not teams:
    st.error("No teams found in th_teams. Seed the teams table first.")
    st.stop()

team_state_map = {row["team_name"]: row for row in team_states}

st.markdown(
    f"""
    <div class="hero-wrap">
        <img class="hero-logo" src="{BALLERS_LOGO}" alt="Ballers League Vol II Logo">
        <div class="hero-title">BALLERS LEAGUE TREASURE HUNT</div>
        <div class="hero-subtitle">Crack the clue. Find the code. Unlock the next stage.</div>
    </div>
    """,
    unsafe_allow_html=True
)

nav1, nav2 = st.columns(2)
with nav1:
    if st.button("Play", use_container_width=True):
        st.session_state.page_mode = "play"
        st.rerun()
with nav2:
    if st.button("Leaderboard", use_container_width=True):
        st.session_state.page_mode = "leaderboard"
        st.rerun()

if st.session_state.page_mode == "leaderboard":
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Treasure Hunt Leaderboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="muted-text">Teams are ranked by exact finish time first. Unfinished teams are ranked by highest tier and then latest progress time.</div>',
        unsafe_allow_html=True
    )

    ranked = sorted(
        team_states,
        key=lambda x: (
            0 if x.get("is_finished") else 1,
            str(x.get("finished_at") or "9999-12-31T23:59:59+00:00"),
            -int(x.get("current_tier", 1)),
            str(x.get("updated_at", "9999-12-31T23:59:59+00:00"))
        )
    )

    st.markdown(
        """
        <div class="leader-row leader-head">
            <div>Rank</div>
            <div>Team</div>
            <div>Tier</div>
            <div>Status</div>
            <div>Finished At</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    for idx, row in enumerate(ranked, start=1):
        team_name = row["team_name"]
        tier = int(row.get("current_tier", 1))
        finished = bool(row.get("is_finished", False))
        rank_class = "rank-pill rank-top" if idx <= 3 else "rank-pill"
        status = "Finished" if finished else "In Progress"
        finished_at = row.get("finished_at")

        if finished_at:
            dt_utc = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
            dt_ist = dt_utc.astimezone(ZoneInfo("Asia/Kolkata"))
            finished_at_display = dt_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
        else:
            finished_at_display = "-"

        st.markdown(
            f"""
            <div class="leader-row">
                <div><div class="{rank_class}">{idx}</div></div>
                <div><strong>{team_name}</strong></div>
                <div>Tier {tier}</div>
                <div>{status}</div>
                <div>{finished_at_display}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if not st.session_state.show_clue:
    st.markdown('<div class="premium-card rules-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <ol>
            <li>Solve the clue carefully.</li>
            <li>Search the mystery location based on the riddle.</li>
            <li>Find the hidden 4-digit code there.</li>
            <li>Enter the code to unlock the football quiz.</li>
            <li>Answer the quiz correctly to unlock the next clue.</li>
            <li>Complete all stages before the other teams. Speed matters.</li>
        </ol>
        <div class="footer-note"><strong>Good luck hunting those extra points.</strong></div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Choose Your Team</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted-text">Tap your team card below to reveal the active clue.</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, team in enumerate(teams):
        row = team_state_map.get(team, {})
        tier = int(row.get("current_tier", 1))
        finished = bool(row.get("is_finished", False))
        max_tier = get_max_tier_for_team(team)
        selected = st.session_state.selected_team == team
        card_class = "team-card team-card-selected" if selected else "team-card"

        with cols[idx % 2]:
            st.markdown('<div class="team-card-wrap">', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="{card_class}">
                    <img class="team-logo" src="{TEAM_LOGOS.get(team, BALLERS_LOGO)}" alt="{team}">
                    <div class="team-name">{team}</div>
                    <div class="team-tier">Tier {tier} / {max_tier}</div>
                    <div class="team-finish">{'Completed' if finished else 'Ready to Hunt'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Select {team}", key=f"team_{team}", use_container_width=True):
                st.session_state.selected_team = team
                st.session_state.show_clue = True
                reset_local_messages()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

selected_team = st.session_state.selected_team
team_state = get_team_state(selected_team)

if not team_state:
    st.error("Team state not found.")
    st.stop()

current_tier = int(team_state["current_tier"])
is_finished = bool(team_state["is_finished"])
max_tier = get_max_tier_for_team(selected_team)
progress_pct = int((current_tier / max_tier) * 100) if max_tier else 0

top_left, top_right = st.columns([3, 1])
with top_left:
    st.markdown(
        f'<div class="team-badge">Team: {selected_team} | Tier {current_tier} / {max_tier}</div>',
        unsafe_allow_html=True
    )
with top_right:
    if st.button("Change Team", use_container_width=True):
        st.session_state.selected_team = None
        st.session_state.show_clue = False
        reset_local_messages()
        st.rerun()

st.markdown(
    f"""
    <div class="progress-wrap">
        <div class="progress-label">Progress: {progress_pct}%</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_pct}%;"></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if is_finished:
    st.success(f"{selected_team} has completed the treasure hunt.")
    st.stop()

clue = get_clue_for_team(selected_team, current_tier)
if not clue:
    st.error(f"No clue assigned for {selected_team} at tier {current_tier}.")
    st.stop()

if clue.get("is_final"):
    st.markdown('<div class="final-card">', unsafe_allow_html=True)
    st.markdown('<div class="final-title">FINAL CLUE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="clue-text">{clue["clue_text"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="clue-title">{clue["clue_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="clue-text">{clue["clue_text"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Unlock Quiz</div>', unsafe_allow_html=True)
st.markdown('<div class="muted-text">Enter the 4-digit code found at the clue location.</div>', unsafe_allow_html=True)

with st.form("pin_form", clear_on_submit=True):
    entered_pin = st.text_input("Enter 4-digit pin", max_chars=4, type="password")
    submitted = st.form_submit_button("Unlock Quiz", use_container_width=True)

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

if "error_msg" in st.session_state:
    st.error(st.session_state["error_msg"])

quiz = get_quiz_for_team(selected_team, current_tier)
quiz_progress = get_quiz_progress(selected_team, current_tier)

quiz_unlocked = bool(quiz_progress and quiz_progress.get("is_unlocked"))
quiz_completed = bool(quiz_progress and quiz_progress.get("is_correct"))

if quiz and quiz_unlocked and not quiz_completed:
    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Football Quiz Gate</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted-text">Answer correctly to unlock the next clue.</div>', unsafe_allow_html=True)

    image_url = quiz.get("image_url")
    if image_url and isinstance(image_url, str) and image_url.strip().lower() not in ["0", "none", "null", ""]:
        try:
            st.image(image_url.strip(), use_container_width=True)
        except Exception:
            st.warning("Quiz image could not be loaded.")

    st.markdown(f"### {quiz['question_text']}")

    answer = st.text_input(
        "Type your answer",
        key=f"quiz_text_{selected_team}_{current_tier}"
    )

    if st.button("Submit Quiz Answer", use_container_width=True):
        if not answer or not answer.strip():
            st.error("Please answer the quiz.")
        else:
            user_answer = normalize_answer(answer)
            correct_answer = normalize_answer(quiz["correct_answer"])

            if user_answer == correct_answer:
                mark_quiz_correct(selected_team, current_tier)
                advance_team(selected_team, current_tier)
                st.success("Correct answer. Next clue unlocked.")
                st.rerun()
            else:
                st.error("Wrong answer. Try again.")

    st.markdown("</div>", unsafe_allow_html=True)
elif quiz and quiz_completed:
    st.success("Quiz completed for this tier.")
