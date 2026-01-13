import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import os
import time
from datetime import datetime
from passlib.context import CryptContext

# --- 1. SETUP & SECURITY ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
logo_path = current_dir / "packers_bears_logo.PNG"
data_file = current_dir / "league_data.csv"
user_file = current_dir / "captains.csv"

# Encryption tool
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# --- 2. DATA FUNCTIONS ---
def load_league_data():
    if data_file.exists():
        df = pd.read_csv(data_file)
        mod_time = os.path.getmtime(data_file)
        return df, datetime.fromtimestamp(mod_time).strftime('%I:%M %p %m/%d/%Y')
    return pd.DataFrame(columns=['Team', 'Wins', 'Losses']), "Never"

def load_captains():
    if user_file.exists():
        return pd.read_csv(user_file)
    # Default admin setup if file is missing
    admin_hash = pwd_context.hash(st.secrets["passwords"]["league_admin"])
    return pd.DataFrame({'username': ['admin'], 'password': [admin_hash]})

def save_csv(df, path):
    df.to_csv(path, index=False)

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="Sussex League", page_icon="🏈", layout="wide")

# Initialize Session State
if 'league_df' not in st.session_state:
    st.session_state.league_df, st.session_state.last_updated = load_league_data()
if 'captains_df' not in st.session_state:
    st.session_state.captains_df = load_captains()

# --- 4. LOGIN LOGIC ---
with st.sidebar:
    if logo_path.exists():
        st.image(Image.open(logo_path), use_container_width=True)
    
    st.title("🔐 Login")
    user_in = st.text_input("Username")
    pass_in = st.text_input("Password", type="password")
    
    auth_level = None
    if user_in and pass_in:
        # Check against the Captains Database
        user_row = st.session_state.captains_df[st.session_state.captains_df['username'] == user_in]
        if not user_row.empty:
            stored_hash = user_row.iloc[0]['password']
            if pwd_context.verify(pass_in, stored_hash):
                auth_level = "admin" if user_in == "admin" else "captain"
                st.success(f"Logged in as {user_in}")
            else:
                st.error("Invalid password")

# --- 5. LEAGUE ADMIN DASHBOARD (CRUD for Captains) ---
if auth_level == "admin":
    st.header("🛠 League Admin: Manage Captains")
    
    # CREATE/UPDATE Captain
    with st.expander("👤 Add/Update a Captain"):
        new_user = st.text_input("Captain Username")
        new_pass = st.text_input("Captain Password", type="password", key="new_cap_pass")
        if st.button("Save Captain"):
            hashed = pwd_context.hash(new_pass)
            if new_user in st.session_state.captains_df['username'].values:
                # Update existing
                idx = st.session_state.captains_df.index[st.session_state.captains_df['username'] == new_user][0]
                st.session_state.captains_df.at[idx, 'password'] = hashed
            else:
                # Create new
                new_entry = pd.DataFrame({'username': [new_user], 'password': [hashed]})
                st.session_state.captains_df = pd.concat([st.session_state.captains_df, new_entry], ignore_index=True)
            save_csv(st.session_state.captains_df, user_file)
            st.success(f"Captain '{new_user}' saved!")
            st.rerun()

    # READ/DELETE Captains
    with st.expander("📋 Current Captains List"):
        st.table(st.session_state.captains_df['username'])
        user_to_del = st.selectbox("Select Captain to Remove", st.session_state.captains_df['username'])
        if st.button("Delete Captain") and user_to_del != "admin":
            st.session_state.captains_df = st.session_state.captains_df[st.session_state.captains_df['username'] != user_to_del]
            save_csv(st.session_state.captains_df, user_file)
            st.warning(f"Removed {user_to_del}")
            st.rerun()

    # ADMIN: Manage Teams
    with st.expander("🏟 Manage League Teams"):
        t_name = st.text_input("New Team Name")
        if st.button("Register Team"):
            if t_name and t_name not in st.session_state.league_df['Team'].values:
                new_row = pd.DataFrame({'Team': [t_name], 'Wins': [0], 'Losses': [0]})
                st.session_state.league_df = pd.concat([st.session_state.league_df, new_row], ignore_index=True)
                save_csv(st.session_state.league_df, data_file)
                st.rerun()

# --- 6. CAPTAIN & ADMIN: Score Entry ---
if auth_level in ["admin", "captain"]:
    st.header("📝 Score Management")
    with st.expander("Update Standings"):
        team_sel = st.selectbox("Select Team", st.session_state.league_df['Team'])
        row = st.session_state.league_df[st.session_state.league_df['Team'] == team_sel].iloc[0]
        c1, c2 = st.columns(2)
        w = c1.number_input("Wins", min_value=0, value=int(row['Wins']))
        l = c2.number_input("Losses", min_value=0, value=int(row['Losses']))
        if st.button("Update Scores"):
            idx = st.session_state.league_df.index[st.session_state.league_df['Team'] == team_sel][0]
            st.session_state.league_df.at[idx, 'Wins'] = w
            st.session_state.league_df.at[idx, 'Losses'] = l
            save_csv(st.session_state.league_df, data_file)
            st.success("Standings updated!")
            time.sleep(1)
            st.rerun()

# --- 7. PUBLIC VIEW ---
st.subheader("Current Standings")
if st.session_state.league_df.empty:
    st.write("No data available.")
else:
    st.table(st.session_state.league_df.sort_values(by=['Wins', 'Losses'], ascending=[False, True]))
    st.caption(f"🕒 Last Update: {st.session_state.last_updated}")

