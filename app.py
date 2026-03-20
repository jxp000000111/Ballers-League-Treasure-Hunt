import streamlit as st

st.set_page_config(page_title="Treasure Hunt", page_icon="🗝️", layout="centered")

TEAM_NAMES = [
    "Amigos FC",
    "Men in Black FC",
    "Timeless Titans",
    "Galacticos 7",
    "Red Devilz",
    "Beast FC",
    "Blue Lock",
]

ROUTE_ASSIGNMENT = {'Amigos FC': 'Route 4', 'Men in Black FC': 'Route 2', 'Timeless Titans': 'Route 7', 'Galacticos 7': 'Route 1', 'Red Devilz': 'Route 5', 'Beast FC': 'Route 3', 'Blue Lock': 'Route 6'}

ROUTE_DATA = {
    "Route 1": {
        "clue_1": {
            "title": "Clue 1",
            "text": """Heroes of the second half enter from here,
With restless legs and an Ole-like impact.
Not quite the battle, not quite the cheer,
Super-sub comes from here to not keep the warmth intact.""",
            "code": "4817",
        },
        "clue_2": {
            "title": "Clue 2",
            "text": """Compared to the rusts and grounds we sit on,
These are some fine upgraded furniture,
Tiptoed on the kitchen, they get to have this rest on,
but unlucky us ballers cant use this for our venture.""",
            "code": "6713",
        },
        "clue_3": {
            "title": "Clue 3",
            "text": """The balls, when shot have seen no boundary,
They fly off high at a missed shot on goal!
They either end up at the roads and debris,
or if we're unlucky, they end up in a flat""",
            "code": "8617",
        },
        "clue_4": {
            "title": "Clue 4",
            "text": """We're all ballers on the pitch alike!
Positions can only make us change unlike.
How to differ ourselves when teams are of same colours,
So take this and distinguish the borders that are very similar.""",
            "code": "5347",
        },
    },
    "Route 2": {
        "clue_1": {
            "title": "Clue 1",
            "text": """The place where you use a lighter,
and the pressure feels a bit lighter.
Mood for a puff is quenched at this spot.
Anywhere else and the vigilance is a bit too hot.""",
            "code": "2639",
        },
        "clue_2": {
            "title": "Clue 2",
            "text": """The unseen grid on our pitch, it's surprising.
Do they know of it's SHOCKING existence? - zilch.
You walk past the grey many times, it's there standing.
Shining lights on our pitch with the turn of a switch.""",
            "code": "4582",
        },
        "clue_3": {
            "title": "Clue 3",
            "text": """Found in the whole wide world, not just this turf.
You gotta see the door before you come in, Sherbert.
Again, make sure you go in the right door enough,
Or else the world will call you a per-""",
            "code": "3049",
        },
        "clue_4": {
            "title": "Clue 4",
            "text": """No crowd sits here, no net is near,
Yet all games start perpendicularly from here.
A perfect spot from where the whole turf is seen,
It’s the place where vision’s more and invention’s mere.""",
            "code": "1784",
        },
    },
    "Route 3": {
        "clue_1": {
            "title": "Clue 1",
            "text": """Seeing yourself from a different angle and accord,
Sometimes it's there, sometimes it's not.
You just pray on a day when its on a proper record,
That you get to score a banger that's hot.""",
            "code": "7154",
        },
        "clue_2": {
            "title": "Clue 2",
            "text": """These hotheads carry us from our houses,
And take us to our home away from home!
These are the only thing that comes to our clutches,
Just like our defences, we get to park it on.""",
            "code": "1936",
        },
        "clue_3": {
            "title": "Clue 3",
            "text": """There are many dhurandhars among us,
One such friendly dhurandhar helps us to fetch ball,
And give water, such a helpful lad he is.
Go and ask him 'Darling Darling dil kyun toda?!'""",
            "code": "6425",
        },
        "clue_4": {
            "title": "Clue 4",
            "text": """All the wagons take a rest here uptight,
Keeping your seats and boots intact.
Hope the Korean stardust caught up just right,
The beast’s rear might just have your redact.""",
            "code": "6921",
        },
    },
    "Route 4": {
        "clue_1": {
            "title": "Clue 1",
            "text": """The neighbours of our sport, you see em all the time.
Don't know if you watch the sport or the chicks!
Feels like an illegit kid of a game of all time,
But the net feels just as low as there's just bricks.""",
            "code": "5928",
        },
        "clue_2": {
            "title": "Clue 2",
            "text": """All the noises of the outer worlds calm,
when you enter through this portal.
Make sure you lock it on your way in to alarm,
Not let a rollin ball go out in total.""",
            "code": "7408",
        },
        "clue_3": {
            "title": "Clue 3",
            "text": """You hit me on my head, its a challenge!
But then you get pissed when you hit my arms!
Players hate me, goalkeepers pray to my avenge,
You'll have to come inside me to win it in a calm.""",
            "code": "9173",
        },
        "clue_4": {
            "title": "Clue 4",
            "text": """I'm filled with something you need only 1 to play.
Say that you want one from me and they deny it.
Only the Academy uses the tools that are in me,
but the hoops and cones crave for the desperate.""",
            "code": "4075",
        },
    },
    "Route 5": {
        "clue_1": {
            "title": "Clue 1",
            "text": """Your thirst find no boundaries here.
You give a call to Resi and get a flagon.
The price to pay for a cooler is mere.
Gonna open, grab one and drink it, then we keep on ballin""",
            "code": "3461",
        },
        "clue_2": {
            "title": "Clue 2",
            "text": """We've known this arena and app for years,
We've called out its name a million times!
Yet for the newcomers to come in and make cheers;
They hoarded the arenas to recognize the good times!""",
            "code": "5284",
        },
        "clue_3": {
            "title": "Clue 3",
            "text": """You play with my elder brothers, but not with me.
They get to stand tall and wide on both ends to take.
I'm just one of the younger ones, a bit skinny and short,
Others would warn you to not hit on me even by mistake :(""",
            "code": "2856",
        },
        "clue_4": {
            "title": "Clue 4",
            "text": """Hit me when I'm white, I count it a goal!
Hit me when I'm black, It's off-target.
But Hit me when I'm Green and the pitch goes split!
I've got the code in my GREEN form, where am I?""",
            "code": "9538",
        },
    },
    "Route 6": {
        "clue_1": {
            "title": "Clue 1",
            "text": """The balls, when shot have seen no boundary,
They fly off high at a missed shot on goal!
They either end up at the roads and debris,
or if we're unlucky, they end up in a flat.""",
            "code": "8245",
        },
        "clue_2": {
            "title": "Clue 2",
            "text": """All the noises of the outer worlds calm,
when you enter through this portal.
Make sure you lock it on your way in to alarm,
Not let a rollin ball go out in total.""",
            "code": "7408",
        },
        "clue_3": {
            "title": "Clue 3",
            "text": """You hit me on my head, its a challenge!
But then you get pissed when you hit my arms!
Players hate me, goalkeepers pray to my avenge,
You'll have to come inside me to win it in a calm.""",
            "code": "9173",
        },
        "clue_4": {
            "title": "Clue 4",
            "text": """Take a look up at the sky, it must be so nice.
A scenario of the sunset as the league goes by.
If you look up and cant see into the abyss.
Then something metal is hiding your view to eye.""",
            "code": "2167",
        },
    },
    "Route 7": {
        "clue_1": {
            "title": "Clue 1",
            "text": """Seeing yourself from a different angle and accord,
Sometimes it's there, sometimes it's not.
You just pray on a day when its on a proper record,
That you get to score a banger that's hot.""",
            "code": "7154",
        },
        "clue_2": {
            "title": "Clue 2",
            "text": """We've known this arena and app for years,
We've called out its name a million times!
Yet for the newcomers to come in and make cheers;
They hoarded the arenas to recognize the good times!""",
            "code": "5284",
        },
        "clue_3": {
            "title": "Clue 3",
            "text": """You play with my elder brothers, but not with me.
They get to stand tall and wide on both ends to take.
I'm just one of the younger ones, a bit skinny and short,
Others would warn you to not hit on me even by mistake :(""",
            "code": "2856",
        },
        "clue_4": {
            "title": "Clue 4",
            "text": """We're all ballers on the pitch alike!
Positions can only make us change unlike.
How to differ ourselves when teams are of same colours,
So take this and distinguish the borders that are very similar.""",
            "code": "5347",
        },
    },
}

if "selected_team" not in st.session_state:
    st.session_state.selected_team = None

if "team_progress" not in st.session_state:
    st.session_state.team_progress = {team: 1 for team in TEAM_NAMES}

if "admin_view" not in st.session_state:
    st.session_state.admin_view = False

def reset_progress():
    st.session_state.selected_team = None
    st.session_state.team_progress = {team: 1 for team in TEAM_NAMES}
    keys_to_remove = [k for k in st.session_state.keys() if k.startswith("code_")]
    for key in keys_to_remove:
        del st.session_state[key]

def get_clue_key(progress: int):
    return {
        1: "clue_1",
        2: "clue_2",
        3: "clue_3",
        4: "clue_4",
    }.get(progress)

st.title("🗝️ Treasure Hunt")
st.write("Choose your team to open your fixed clue route.")

with st.sidebar:
    st.header("Admin")
    admin_password = st.text_input("Admin password", type="password")
    if st.button("Reset Progress", use_container_width=True):
        if admin_password == "9090":
            reset_progress()
            st.success("All team progress has been reset.")
        else:
            st.error("Incorrect admin password.")
    if st.checkbox("Show fixed route assignment", value=False):
        if admin_password == "9090":
            st.session_state.admin_view = True
        else:
            st.session_state.admin_view = False
            st.warning("Enter correct admin password to view route assignment.")

if st.session_state.admin_view:
    st.markdown("---")
    st.subheader("Fixed Team Route Assignment")
    for team_name in TEAM_NAMES:
        route_name = ROUTE_ASSIGNMENT[team_name]
        st.write(f"**{team_name}** → {route_name}")

st.markdown("---")
st.subheader("Select Your Team")

cols = st.columns(3)
for i, team_name in enumerate(TEAM_NAMES):
    with cols[i % 3]:
        if st.button(team_name, use_container_width=True):
            st.session_state.selected_team = team_name

selected_team = st.session_state.selected_team

if selected_team:
    route_name = ROUTE_ASSIGNMENT[selected_team]
    route = ROUTE_DATA[route_name]
    progress = st.session_state.team_progress[selected_team]

    st.markdown("---")
    st.subheader(selected_team)
    st.caption(f"Your progress: Step {progress} of 4")

    if progress in [1, 2, 3, 4]:
        clue_key = get_clue_key(progress)
        clue = route[clue_key]

        st.markdown(f"### {clue['title']}")
        st.info(clue["text"])

        entered_code = st.text_input(
            "Enter the 4-digit code",
            max_chars=4,
            type="password",
            key=f"code_{selected_team}_{clue_key}",
            placeholder="Enter code",
        )

        if st.button(f"Unlock Next Clue for {selected_team}", use_container_width=True):
            if not entered_code.isdigit() or len(entered_code) != 4:
                st.error("Please enter a valid 4-digit code.")
            elif entered_code == clue["code"]:
                st.session_state.team_progress[selected_team] += 1
                if st.session_state.team_progress[selected_team] == 5:
                    st.success("Correct code. Route completed.")
                else:
                    st.success("Correct code. Moving to the next clue.")
                st.rerun()
            else:
                st.error("Incorrect code. Try again.")

    elif progress == 5:
        st.success("You have completed your full route.")
        st.write("Please report to the organizers.")
