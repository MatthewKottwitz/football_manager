import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import os
import time
import random
import string
from datetime import datetime
from passlib.context import CryptContext

# --- 1. SETUP ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
logo_path = current_dir / "packers_bears_logo.PNG"
data_file = current_dir / "league_data.csv"
user_file = current_dir / "captains.csv"
invite_file = current_dir / "invites.csv" # New file for one-time codes

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# --- 2. DATA FUNCTIONS ---
def load_csv(path, columns):
    if Path(path).exists():
        return pd.read_csv(path)
    return pd.DataFrame(columns=columns)

def save_csv(df, path):
    df.to_csv(path, index=False)

# Initialize Session State
if 'league_df' not in st.session_state:
    if data_file.exists():
        st.session_state.league_df = pd.read_csv(data_file)
    else:
        st.session_state.league_df = pd.DataFrame(columns=['Team', 'Wins', 'Losses'])

if 'captains_df' not in st.session_state:
    st.session_state.captains_df = load_csv(user_file, ['username', 'password'])
    # Ensure admin exists
    if 'admin' not in st.session_state.captains_df['username'].values:
        admin_hash = pwd_context.hash(st.secrets["passwords"]["league_admin"])
        admin_df = pd.DataFrame({'username': ['admin'], 'password': [admin_hash]})
        st.session_state.captains_df = pd.concat([st.session_state.captains_df, admin_df], ignore_index=True)
        save_csv(st.session_state.captains_df, user_file)

if 'invites_df' not in st.session_state:
    st.session_state.invites_df = load_csv(invite_file, ['code'])

# --- 3. SIDEBAR ---
auth_level = None
with st.sidebar:
    if logo_path.exists():
        st.image(Image.open(logo_path), use_container_width=True)
    
    mode = st.radio("Access", ["Login", "Register with Invite Code"])

    if mode == "Login":
        st.title("🔐 Login")
        u_in = st.text_input("Username")
        p_in = st.text_input("Password", type="password")
        if st.button("Sign In"):
            user_row = st.session_state.captains_df[st.session_state.captains_df['username'] == u_in]
            if not user_row.empty and pwd_context.verify(p_in, user_row.iloc[0]['password']):
                st.session_state.logged_in_user = u_in
                st.session_state.auth_level = "admin" if u_in == "admin" else "captain"
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        st.title("🎟 Register")
        code_in = st.text_input("One-Time Invite Code")
        if code_in in st.session_state.invites_df['code'].values:
            st.success("Code Valid!")
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password", type="password")
            if st.button("Create Account"):
                if new_u and new_p and new_u not in st.session_state.captains_df['username'].values:
                    # Save User
                    hashed = pwd_context.hash(new_p)
                    new_user_df = pd.DataFrame({'username': [new_u], 'password': [hashed]})
                    st.session_state.captains_df = pd.concat([st.session_state.captains_df, new_user_df], ignore_index=True)
                    save_csv(st.session_state.captains_df, user_file)
                    # Remove Code (One-time use!)
                    st.session_state.invites_df = st.session_state.invites_df[st.session_state.invites_df['code'] != code_in]
                    save_csv(st.session_state.invites_df, invite_file)
                    st.success("Account created! Now go to Login.")
                    time.sleep(2)
                    st.rerun()
        elif code_in:
            st.error("Code used or invalid.")

    if 'auth_level' in st.session_state:
        auth_level = st.session_state.auth_level
        if st.button("Logout"):
            del st.session_state.auth_level
            st.rerun()

# --- 4. ADMIN DASHBOARD ---
if auth_level == "admin":
    st.header("🛠 League Admin Console")
    
    # INVITE GENERATOR
    with st.expander("🎟 Generate One-Time Invite Code"):
        if st.button("Create New Code"):
            new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            new_code_df = pd.DataFrame({'code': [new_code]})
            st.session_state.invites_df = pd.concat([st.session_state.invites_df, new_code_df], ignore_index=True)
            save_csv(st.session_state.invites_df, invite_file)
            st.code(new_code) # Displays the code for you to copy
            st.info("Text this code to the captain. It will expire after one use.")

    # USER MANAGEMENT (THE "KICK" BUTTON)
    with st.expander("👤 Manage Captain Accounts"):
        st.write("Active Captains:")
        for user in st.session_state.captains_df['username']:
            if user != 'admin':
                col1, col2 = st.columns([3, 1])
                col1.text(user)
                if col2.button("Remove Access", key=user):
                    st.session_state.captains_df = st.session_state.captains_df[st.session_state.captains_df['username'] != user]
                    save_csv(st.session_state.captains_df, user_file)
                    st.rerun()

    # TEAM MANAGEMENT
    with st.expander("🏟 Manage Teams"):
        t_name = st.text_input("New Team Name")
        if st.button("Add Team"):
            if t_name and t_name not in st.session_state.league_df['Team'].values:
                new_row = pd.DataFrame({'Team': [t_name], 'Wins': [0], 'Losses': [0]})
                st.session_state.league_df = pd.concat([st.session_state.league_df, new_row], ignore_index=True)
                save_csv(st.session_state.league_df, data_file)
                st.rerun()

# --- 5. SCORE UPDATES (ADMIN & CAPTAINS) ---
if auth_level:
    st.header("📝 Score Management")
    with st.expander("Update Standings"):
        team_sel = st.selectbox("Select Team", st.session_state.league_df['Team'])
        if not st.session_state.league_df.empty:
            row = st.session_state.league_df[st.session_state.league_df['Team'] == team_sel].iloc[0]
            c1, c2 = st.columns(2)
            w = c1.number_input("Wins", min_value=0, value=int(row['Wins']))
            l = c2.number_input("Losses", min_value=0, value=int(row['Losses']))
            if st.button("Update"):
                idx = st.session_state.league_df.index[st.session_state.league_df['Team'] == team_sel][0]
                st.session_state.league_df.at[idx, 'Wins'] = w
                st.session_state.league_df.at[idx, 'Losses'] = l
                save_csv(st.session_state.league_df, data_file)
                st.success("Standings updated!")
                time.sleep(1)
                st.rerun()

# --- 6. STANDINGS ---
st.subheader("🏈 Live Standings")
if not st.session_state.league_df.empty:
    st.table(st.session_state.league_df.sort_values(by=['Wins', 'Losses'], ascending=[False, True]))
else:
    st.write("No teams registered yet.")
