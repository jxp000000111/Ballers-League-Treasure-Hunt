import sqlite3
import streamlit as st

st.set_page_config(page_title="Treasure Hunt", page_icon="🗝️", layout="centered")

# -------------------------------------------------
# BACKEND CONFIGURATION
# Edit clue texts and PINs as needed
# IMPORTANT:
# - clue_1, clue_2 and clue_3 are now pools of unique clues
# - final_clue remains common for all users
# -------------------------------------------------
CLUE_POOLS = {
    "clue_1": [
        "Clue 1A: Start near the left goalpost and count five steps toward the center.",
        "Clue 1B: Look beneath the bench closest to the halfway line.",
        "Clue 1C: Search where the captain usually stands before kickoff.",
        "Clue 1D: Find the cone nearest to the corner flag and check behind it.",
        "Clue 1E: Look near the midfield line where the chalk is brightest.",
        "Clue 1F: Search beside the practice bibs near the sideline.",
        "Clue 1G: Check the far post area where missed shots often land.",
    ],
    "clue_2": [
        "Clue 2A: The next hint hides where muddy boots are usually left behind.",
        "Clue 2B: Look around the water break area near the touchline.",
        "Clue 2C: Search the third seat from the right on the substitute bench.",
        "Clue 2D: Check the training marker nearest the center circle.",
        "Clue 2E: Look near the bag of spare balls by the dugout.",
        "Clue 2F: Search under the towel nearest the coaching area.",
    ],
    "clue_3": [
        "Clue 3A: Go where the loudest whistle echoes and inspect the boundary.",
        "Clue 3B: Look at the shadow side of the scoreboard or notice board.",
        "Clue 3C: Check near the equipment bag resting by the sideline.",
        "Clue 3D: The clue waits close to the farthest corner arc.",
        "Clue 3E: Search by the cone placed nearest the referee’s usual path.",
    ],
}

FINAL_CLUE_TEXT = "Final clue: The treasure rests where every match begins, but never stays for long."

PINS = {
    "clue_2": "4821",
    "clue_3": "7354",
    "final_clue": "9167",
}

DB_FILE = "treasure_hunt.db"


# -------------------------------------------------
# DATABASE HELPERS
# -------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            clue_1 TEXT,
            clue_2 TEXT,
            clue_3 TEXT,
            unlocked_clue_1 INTEGER DEFAULT 0,
            unlocked_clue_2 INTEGER DEFAULT 0,
            unlocked_clue_3 INTEGER DEFAULT 0,
            unlocked_final_clue INTEGER DEFAULT 0
        )
        """
    )

    conn.commit()
    conn.close()


def get_user(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def get_used_clues(column_name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {column_name} FROM users WHERE {column_name} IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return {row[0] for row in rows if row[0]}


def assign_unique_clue(username: str, clue_key: str):
    used = get_used_clues(clue_key)
    available = [clue for clue in CLUE_POOLS[clue_key] if clue not in used]

    if not available:
        return None

    assigned_clue = available[0]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {clue_key} = ? WHERE username = ?", (assigned_clue, username))
    conn.commit()
    conn.close()
    return assigned_clue


def create_user_if_needed(username: str):
    existing_user = get_user(username)
    if existing_user:
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

    # Only assign Clue 1 initially.
    # Clue 2 and Clue 3 are assigned only when a team actually reaches that round.
    assign_unique_clue(username, "clue_1")


def get_user_record(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT username, clue_1, clue_2, clue_3,
               unlocked_clue_1, unlocked_clue_2, unlocked_clue_3, unlocked_final_clue
        FROM users
        WHERE username = ?
        """,
        (username,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def set_unlocked(username: str, clue_key: str):
    column_map = {
        "clue_1": "unlocked_clue_1",
        "clue_2": "unlocked_clue_2",
        "clue_3": "unlocked_clue_3",
        "final_clue": "unlocked_final_clue",
    }
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE users SET {column_map[clue_key]} = 1 WHERE username = ?",
        (username,),
    )
    conn.commit()
    conn.close()


def reset_all_progress():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    conn.commit()
    conn.close()


# -------------------------------------------------
# SESSION STATE SETUP
# -------------------------------------------------
init_db()

if "selected_clue" not in st.session_state:
    st.session_state.selected_clue = None

if "active_user" not in st.session_state:
    st.session_state.active_user = ""


# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------
def select_clue(clue_key: str):
    st.session_state.selected_clue = clue_key


def verify_pin(clue_key: str, entered_pin: str):
    return PINS[clue_key] == entered_pin


def login_user():
    st.subheader("Enter your user name / team name")
    username = st.text_input("User ID", placeholder="Example: Team Alpha")

    if st.button("Start Hunt", use_container_width=True):
        cleaned = username.strip()
        if not cleaned:
            st.error("Please enter a valid user name or team name.")
        else:
            create_user_if_needed(cleaned)
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
    username = st.session_state.active_user
    if not username:
        return

    clue_key = st.session_state.selected_clue
    if not clue_key:
        return

    record = get_user_record(username)
    if not record:
        st.error("User record not found.")
        return

    _, clue_1_text, clue_2_text, clue_3_text, unlocked_1, unlocked_2, unlocked_3, unlocked_final = record

    st.markdown("---")
    title_map = {
        "clue_1": "Clue 1",
        "clue_2": "Clue 2",
        "clue_3": "Clue 3",
        "final_clue": "Final Clue",
    }
    st.subheader(title_map[clue_key])

    # Sequential locking rules
    if clue_key == "clue_2" and not unlocked_1:
        st.warning("You must unlock Clue 1 first.")
        return
    if clue_key == "clue_3" and not unlocked_2:
        st.warning("You must unlock Clue 2 first.")
        return
    if clue_key == "final_clue" and not unlocked_3:
        st.warning("You must unlock Clue 3 first.")
        return

    # Clue 1 unlocks directly
    if clue_key == "clue_1":
        if not clue_1_text:
            st.error("No unique Clue 1 is available. Add more clues to the pool.")
            return
        set_unlocked(username, "clue_1")
        st.success("Unlocked successfully.")
        st.info(clue_1_text)
        return

    # Already unlocked clues
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

        # Assign round-limited clues only when a team reaches that round.
        if clue_key == "clue_2" and not clue_2_text:
            clue_2_text = assign_unique_clue(username, "clue_2")
            if not clue_2_text:
                st.error("No Clue 2 is available. This team reached too late and is eliminated.")
                return

        if clue_key == "clue_3" and not clue_3_text:
            clue_3_text = assign_unique_clue(username, "clue_3")
            if not clue_3_text:
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


# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🗝️ Treasure Hunt App")
st.write(
    "Each user gets a unique clue for Clue 1, Clue 2 and Clue 3. The final clue is common for everyone."
)

with st.sidebar:
    st.header("Admin Panel")
    st.caption("Use this only during testing or event setup.")
    if st.button("Reset All Users and Clues"):
        reset_all_progress()
        st.session_state.active_user = ""
        st.session_state.selected_clue = None
        st.success("All users and clue assignments have been reset.")

if not st.session_state.active_user:
    login_user()
else:
    st.success(f"Logged in as: {st.session_state.active_user}")
    show_clue_buttons()
    show_selected_clue()

st.markdown("---")
st.caption(
    "This version is round-limited: 7 unique clues for Clue 1, 6 for Clue 2, 5 for Clue 3, and one shared final clue. Teams that arrive after the available clues are exhausted are eliminated."
)
