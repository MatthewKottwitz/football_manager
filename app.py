import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import os
import time

# --- 1. FILE PATH SETUP ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
logo_path = current_dir / "packers_bears_logo.PNG"
data_file = current_dir / "league_data.csv"

# --- 2. PAGE CONFIGURATION ---
if logo_path.exists():
    try:
        img = Image.open(logo_path)
        st.set_page_config(page_title="League Manager", page_icon=img, layout="wide")
    except Exception:
        st.set_page_config(page_title="League Manager", page_icon="🏈", layout="wide")
else:
    st.set_page_config(page_title="League Manager", page_icon="🏈", layout="wide")

# --- 3. DATA PERSISTENCE FUNCTIONS ---
def load_data():
    if data_file.exists():
        return pd.read_csv(data_file)
    return pd.DataFrame(columns=['Team', 'Wins', 'Losses'])

def save_data(df):
    df.to_csv(data_file, index=False)

# Load data into session state
if 'league_df' not in st.session_state:
    st.session_state.league_df = load_data()

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
    
    # ADD NEW TEAM
    with st.expander("➕ Add New Team", expanded=False):
        # We use a unique key to help with clearing
        new_team = st.text_input("Team Name", key="new_team_input")
        if st.button("Confirm Add Team"):
            if new_team and new_team not in st.session_state.league_df['Team'].values:
                new_row = pd.DataFrame({'Team': [new_team], 'Wins': [0], 'Losses': [0]})
                st.session_state.league_df = pd.concat([st.session_state.league_df, new_row], ignore_index=True)
                save_data(st.session_state.league_df)
                
                # Feedback
                st.success(f"✅ {new_team} added successfully!")
                time.sleep(1) # Give user a moment to see the message
                st.rerun() # This clears the text_input box
            else:
                st.error("Error: Team already exists or name is empty.")

    # UPDATE SCORES
    if not st.session_state.league_df.empty:
        with st.expander("📝 Update Scores", expanded=False):
            team_to_edit = st.selectbox("Select Team", st.session_state.league_df['Team'])
            current_row = st.session_state.league_df[st.session_state.league_df['Team'] == team_to_edit].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                new_wins = st.number_input("Wins", min_value=0, value=int(current_row['Wins']), step=1)
            with col2:
                new_losses = st.number_input("Losses", min_value=0, value=int(current_row['Losses']), step=1)
            
            if st.button("Update League Table"):
                idx = st.session_state.league_df.index[st.session_state.league_df['Team'] == team_to_edit][0]
                st.session_state.league_df.at[idx, 'Wins'] = new_wins
                st.session_state.league_df.at[idx, 'Losses'] = new_losses
                save_data(st.session_state.league_df)
                
                st.success(f"✅ Updated {team_to_edit} scores!")
                time.sleep(1)
                st.rerun()

    # RESET LEAGUE
    with st.expander("🚨 Danger Zone"):
        st.write("This will permanently delete all teams and scores.")
        if st.button("Wipe All Data"):
            st.session_state.league_df = pd.DataFrame(columns=['Team', 'Wins', 'Losses'])
            save_data(st.session_state.league_df)
            st.warning("League data cleared.")
            time.sleep(1)
            st.rerun()
else:
    # Auto-refresh data for players to see the latest PC updates
    st.session_state.league_df = load_data()
    st.info("Log in as Admin to manage the league.")

# --- 6. DISPLAY TABLE ---
st.subheader("Current Standings")
if st.session_state.league_df.empty:
    st.write("The league is currently empty.")
else:
    # Sort by Wins (Highest First), then by Losses (Lowest First)
    sorted_df = st.session_state.league_df.sort_values(by=['Wins', 'Losses'], ascending=[False, True])
    st.table(sorted_df)
