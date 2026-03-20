# Treasure Hunt Streamlit App

A public Streamlit app for a multi-team treasure hunt.

## Features

- Team-based login
- Unique clue allocation for Clue 1, Clue 2, and Clue 3
- Sequential locking between rounds
- Elimination logic:
  - 7 teams can receive Clue 1
  - 6 teams can receive Clue 2
  - 5 teams can receive Clue 3
  - Final clue is shared
- Google Sheets backend for persistent shared state
- Admin reset option protected by password

## Project structure

```text
treasure_hunt_streamlit_project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

## Google Sheet setup

Create one Google Sheet with these tabs:

- `users`
- `clue_1_pool`
- `clue_2_pool`
- `clue_3_pool`

### users sheet header

```text
username | clue_1 | clue_2 | clue_3 | unlocked_clue_1 | unlocked_clue_2 | unlocked_clue_3 | unlocked_final_clue | eliminated
```

### clue pool sheet header

```text
clue_text | assigned_to
```

Fill the clue pools like this:

- `clue_1_pool` -> 7 clue rows
- `clue_2_pool` -> 6 clue rows
- `clue_3_pool` -> 5 clue rows

Leave `assigned_to` blank.

## Streamlit secrets

Create `.streamlit/secrets.toml` locally using the example file.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select your repo, branch, and `app.py`.
5. Add the values from `secrets.toml.example` into the app Secrets section.
6. Share the Google Sheet with the service account email as Editor.
7. Deploy.

## Notes

Google Sheets is fine for small live events. For stricter high-concurrency competitions, a transactional backend like Supabase/Postgres is stronger.
