import streamlit as st
import pandas as pd
from datetime import date
from scheduler import generate_schedule
from PIL import Image
import os

# Get the directory that app.py is in
img_dir = os.path.dirname(__file__)
image_path = os.path.join(img_dir, "logo.png")

try:
    # Open the image using Pillow
    logo_image = Image.open(image_path)
    
    st.set_page_config(
        page_title="League Manager",
        page_icon=logo_image, # This sets the browser tab icon
        layout="wide"
    )
    
    # Also show it in the sidebar
    st.sidebar.image(logo_image, width=150)

except Exception as e:
    # If the file is still being "stubborn", fallback to emoji
    st.set_page_config(page_title="League Manager", page_icon="🏈")
    st.sidebar.warning("Logo file not found, using default.")

st.set_page_config(page_title="Football Scheduler", layout="wide")
st.sidebar.image("packers_bears_logo.png", width=100)

st.title("🏈 Football League Manager")

# Sidebar - Setup
with st.sidebar:
    st.header("League Configuration")
    team_input = st.text_area("Enter Team Names (one per line):", 
                             value="Tigers\nLions\nEagles\nBears")
    start_date = st.date_input("Start Date", date.today())
    
    if st.button("Generate/Reset Schedule"):
        teams = [t.strip() for t in team_input.split('\n') if t.strip()]
        data = generate_schedule(teams, start_date)
        st.session_state.df = pd.DataFrame(data)

# Main App Logic
if 'df' in st.session_state:
    st.subheader("Match Schedule & Scores")
    st.info("Edit the 'Home Score' and 'Away Score' columns below to update standings.")
    
    # Editable Table
    edited_df = st.data_editor(st.session_state.df, use_container_width=True, hide_index=True)
    st.session_state.df = edited_df

    # Calculate Standings
    st.divider()
    st.subheader("League Standings")
    
    # Simple Standing Logic inside App for speed
    stats = {}
    teams = pd.concat([edited_df['Home Team'], edited_df['Away Team']]).unique()
    for t in teams: stats[t] = {'GP':0, 'W':0, 'D':0, 'L':0, 'Pts':0}
    
    for _, r in edited_df.iterrows():
        stats[r['Home Team']]['GP'] += 1
        stats[r['Away Team']]['GP'] += 1
        if r['Home Score'] > r['Away Score']:
            stats[r['Home Team']]['W'] += 1; stats[r['Home Team']]['Pts'] += 3
            stats[r['Away Team']]['L'] += 1
        elif r['Away Score'] > r['Home Score']:
            stats[r['Away Team']]['W'] += 1; stats[r['Away Team']]['Pts'] += 3
            stats[r['Home Team']]['L'] += 1
        else:
            stats[r['Home Team']]['D'] += 1; stats[r['Home Team']]['Pts'] += 1
            stats[r['Away Team']]['D'] += 1; stats[r['Away Team']]['Pts'] += 1
            
    standings_df = pd.DataFrame.from_dict(stats, orient='index').sort_values('Pts', ascending=False)
    st.table(standings_df)

    # Download Option
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Schedule (CSV)", csv, "schedule.csv", "text/csv")
else:

    st.write("Enter teams in the sidebar and click 'Generate' to begin.")


