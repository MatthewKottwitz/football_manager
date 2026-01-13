import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import os

# --- 1. FILE PATH SETUP ---
# This finds the folder where app.py lives
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
# We use the EXACT name you found on GitHub (all lowercase with .PNG)
logo_path = current_dir / "packers_bears_logo.PNG"

# --- 2. PAGE CONFIGURATION (Must be the first Streamlit command) ---
if logo_path.exists():
    try:
        img = Image.open(logo_path)
        st.set_page_config(
            page_title="Sussex Football League",
            page_icon=img,
            layout="wide"
        )
    except Exception:
        # Fallback if the image file is corrupted
        st.set_page_config(page_title="Sussex Football League", page_icon="🏈", layout="wide")
else:
    # Fallback if the file is missing
    st.set_page_config(page_title="Sussex Football League", page_icon="🏈", layout="wide")

# --- 3. SIDEBAR & LOGO DISPLAY ---
with st.sidebar:
    if logo_path.exists():
        st.image(Image.open(logo_path), use_container_width=True)
    
    st.title("League Admin")
    st.divider()
    
    # --- ADMIN PASSWORD SECTION ---
    # Change "sussex2026" to whatever password you want!
    admin_password = "sussex2026" 
    user_password = st.text_input("Enter Admin Password", type="password")
    
    is_admin = (user_password == admin_password)
    
    if is_admin:
        st.success("Admin Access Granted")
    else:
        st.info("Enter password to unlock editing tools.")

# --- 4. MAIN APP CONTENT ---
st.title("🏈 Sussex Football League Manager")

if is_admin:
    st.header("Admin Control Panel")
    
    # Create two columns for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate New Schedule"):
            st.write("Schedule generated!")
            # Add your schedule generation logic here

    with col2:
        # Check if we are in the "confirming" state
        if 'confirm_reset' not in st.session_state:
            st.session_state.confirm_reset = False

        if not st.session_state.confirm_reset:
            if st.button("Reset All Scores"):
                st.session_state.confirm_reset = True
                st.rerun() # Refresh to show the confirmation buttons
        else:
            # This shows ONLY after they click the first 'Reset' button
            st.warning("⚠️ Are you absolutely sure? This cannot be undone.")
            sub_col1, sub_col2 = st.columns(2)
            
            with sub_col1:
                if st.button("✅ YES, Reset Everything"):
                    # --- PLACE YOUR RESET LOGIC HERE ---
                    st.success("All scores have been wiped.")
                    st.session_state.confirm_reset = False # Reset the state
                    # st.rerun() 
                    
            with sub_col2:
                if st.button("❌ NO, Cancel"):
                    st.session_state.confirm_reset = False
                    st.rerun()

else:
    # What the regular parents/players see
    st.info("Welcome! View the current standings and schedule below.")

# --- 5. YOUR DATA LOGIC (Example Table) ---
st.subheader("Current Standings")
# (This is where your pandas dataframe code would go)
data = {
    'Team': ['Packers', 'Bears', 'Lions', 'Vikings'],
    'Wins': [10, 2, 5, 4],
    'Losses': [0, 8, 5, 6]
}
df = pd.DataFrame(data)
st.table(df)

