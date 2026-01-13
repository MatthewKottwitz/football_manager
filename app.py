import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import os

# --- 1. FILE PATH SETUP ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
logo_path = current_dir / "packers_bears_logo.PNG"

# --- 2. PAGE CONFIGURATION ---
if logo_path.exists():
    try:
        img = Image.open(logo_path)
        st.set_page_config(page_title="League Manager", page_icon=img, layout="wide")
    except Exception:
        st.set_page_config(page_title="League Manager", page_icon="🏈", layout="wide")
else:
    st.set_page_config(page_title="League Manager", page_icon="🏈", layout="wide")

# --- 3. DATA INITIALIZATION (The "Database") ---
if 'league_df' not in st.session_state:
    # Start with an empty table with the correct columns
    st.session_state.league_df = pd.DataFrame(columns=['Team', 'Wins', 'Losses'])

# --- 4. SIDEBAR & ADMIN AUTH ---
with st.sidebar:
    if logo_path.exists():
        st.image(Image.open(logo_path), use_container_width=True)
    
    st.title("League Admin")
    admin_password = "sussex2026" 
    user_password = st.text_input("Enter Admin Password", type="password")
    is_admin = (user_password == admin_password)

# --- 5. MAIN CONTENT ---
st.title("🏈 Sussex Football League Manager")

if is_admin:
    st.header("Admin Control Panel")
    
    # --- TAB 1: ADD TEAMS ---
    with st.expander("➕ Add New Team"):
        new_team = st.text_input("Team Name")
        if st.button("Add Team"):
            if new_team and new_team not in st.session_state.league_df['Team'].values:
                new_row = pd.DataFrame({'Team': [new_team], 'Wins': [0], 'Losses': [0]})
                st.session_state.league_df = pd.concat([st.session_state.league_df, new_row], ignore_index=True)
                st.success(f"Added {new_team}")
                st.rerun()
            else:
                st.warning("Team already exists or name is empty.")

    # --- TAB 2: UPDATE SCORES ---
    if not st.session_state.league_df.empty:
        with st.expander("📝 Update Scores"):
            team_to_edit = st.selectbox("Select Team", st.session_state.league_df['Team'])
            col1, col2 = st.columns(2)
            with col1:
                new_wins = st.number_input("Wins", min_value=0, step=1)
            with col2:
                new_losses = st.number_input("Losses", min_value=0, step=1)
            
            if st.button("Save Score"):
                idx = st.session_state.league_df.index[st.session_state.league_df['Team'] == team_to_edit][0]
                st.session_state.league_df.at[idx, 'Wins'] = new_wins
                st.session_state.league_df.at[idx, 'Losses'] = new_losses
                st.success(f"Updated {team_to_edit}")
                st.rerun()

    # --- TAB 3: RESET ---
    with st.expander("🚨 Danger Zone"):
        if st.button("Reset Entire League"):
            st.session_state.league_df = pd.DataFrame(columns=['Team', 'Wins', 'Losses'])
            st.rerun()
else:
    st.info("Log in as Admin to add teams or edit scores.")

# --- 6. DISPLAY TABLE ---
st.subheader("Current Standings")
if st.session_state.league_df.empty:
    st.write("No teams added yet. Admin must add teams to see the leaderboard.")
else:
    # Sort by Wins (Descending)
    sorted_df = st.session_state.league_df.sort_values(by='Wins', ascending=False)
    st.table(sorted_df)
