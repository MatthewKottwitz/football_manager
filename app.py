import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import os
import time
from datetime import datetime

# --- 1. FILE PATH SETUP ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
logo_path = current_dir / "packers_bears_logo.PNG"
data_file = current_dir / "league_data.csv"

# --- 2. PAGE CONFIGURATION ---
if logo_path.exists():
    try:
        img = Image.open(logo_path)
        st.set_page_config(page_title="Sussex League", page_icon=img, layout="wide")
    except Exception:
        st.set_page_config(page_title="Sussex League", page_icon="🏈", layout="wide")
else:
    st.set_page_config(page_title="Sussex League", page_icon="🏈", layout="wide")

# --- 3. DATA PERSISTENCE FUNCTIONS ---
def load_data():
    if data_file.exists():
        df = pd.read_csv(data_file)
        # Get the last modified time of the file for the timestamp
        mod_time = os.path.getmtime(data_file)
        last_update = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %I:%M %p')
        return df, last_update
    return pd.DataFrame(columns=['Team', 'Wins', 'Losses']), "Never"

def save_data(df):
    df.to_csv(data_file, index=False)

# Initial load
if 'league_df' not in st.session_state:
    st.session_state.league_df, st.session_state.last_updated = load_data()

# --- 4. SIDEBAR & SECURITY ---
with st.sidebar:
    if logo_path.exists():
        st.image(Image.open(logo_path), use_container_width=True)
    
    st.title("Admin Access")
    
    # SECURITY: This pulls the password from Streamlit's "Secrets" vault
    # instead of being written in the code for everyone on GitHub to see.
    try:
        admin_password = st.secrets["admin_password"]
    except KeyError:
        st.error("Secret 'admin_password' not set in Streamlit Cloud Settings!")
        admin_password = None

    user_password = st.text_input("Password", type="password")
    is_admin = (admin_password and user_password == admin_password)

# --- 5. MAIN CONTENT ---
st.title("🏈 Sussex Football League")

if is_admin:
    st.header("Admin Dashboard")
    
    # Form: Add New Team
    with st.expander("➕ Add New Team"):
        new_name = st.text_input("Enter Team Name", key="team_in")
        if st.button("Save Team"):
            if new_name and new_name not in st.session_state.league_df['Team'].values:
                new_row = pd.DataFrame({'Team': [new_name], 'Wins': [0], 'Losses': [0]})
                st.session_state.league_df = pd.concat([st.session_state.league_df, new_row], ignore_index=True)
                save_data(st.session_state.league_df)
                st.success(f"Success! {new_name} has been added.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid name or team already exists.")

    # Form: Update Scores
    if not st.session_state.league_df.empty:
        with st.expander("📝 Update Scores"):
            team_sel = st.selectbox("Select Team", st.session_state.league_df['Team'])
            row = st.session_state.league_df[st.session_state.league_df['Team'] == team_sel].iloc[0]
            
            c1, c2 = st.columns(2)
            w = c1.number_input("Total Wins", min_value=0, value=int(row['Wins']))
            l = c2.number_input("Total Losses", min_value=0, value=int(row['Losses']))
            
            if st.button("Update Scores"):
                idx = st.session_state.league_df.index[st.session_state.league_df['Team'] == team_sel][0]
                st.session_state.league_df.at[idx, 'Wins'] = w
                st.session_state.league_df.at[idx, 'Losses'] = l
                save_data(st.session_state.league_df)
                st.success(f"Scores updated for {team_sel}!")
                time.sleep(1)
                st.rerun()

    # Form: Reset
    with st.expander("🚨 Reset Data"):
        if st.button("Delete Everything"):
            st.session_state.league_df = pd.DataFrame(columns=['Team', 'Wins', 'Losses'])
            save_data(st.session_state.league_df)
            st.warning("All data deleted.")
            time.sleep(1)
            st.rerun()
else:
    # Auto-sync data for non-admins
    st.session_state.league_df, st.session_state.last_updated = load_data()
    st.info("Log in as Admin to edit the standings.")

# --- 6. DISPLAY TABLE ---
st.subheader("Current Standings")
if st.session_state.league_df.empty:
    st.write("No data available yet.")
else:
    # Sort by Wins (High to Low), then Losses (Low to High)
    display_df = st.session_state.league_df.sort_values(by=['Wins', 'Losses'], ascending=[False, True])
    st.table(display_df)
    st.caption(f"🕒 Last data update: {st.session_state.last_updated}")
