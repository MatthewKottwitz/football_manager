from datetime import timedelta

def generate_schedule(teams, start_date):
    # Handle odd number of teams by adding a placeholder
    if len(teams) % 2 != 0:
        teams.append("BYE")

    n = len(teams)
    schedule_data = []
    temp_teams = list(teams)

    # Round Robin: Every team plays n-1 matches
    for round_num in range(n - 1):
        week_date = start_date + timedelta(weeks=round_num)
        for i in range(n // 2):
            home = temp_teams[i]
            away = temp_teams[n - 1 - i]
            
            # Don't show games involving the "BYE" placeholder
            if home != "BYE" and away != "BYE":
                schedule_data.append({
                    "Week": round_num + 1,
                    "Date": week_date.strftime("%Y-%m-%d"),
                    "Home Team": home,
                    "Away Team": away,
                    "Home Score": 0,
                    "Away Score": 0
                })
        
        # Rotate teams (keep index 0 fixed)
        temp_teams = [temp_teams[0]] + [temp_teams[-1]] + temp_teams[1:-1]
        
    return schedule_data

def calculate_standings(df):
    # Get unique team names (excluding BYE)
    teams = sorted(list(set(df['Home Team']).union(set(df['Away Team']))))
    standings = {team: {'GP': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}

    for _, row in df.iterrows():
        h, a = row['Home Team'], row['Away Team']
        hs, ascore = row['Home Score'], row['Away Score']

        # We assume scores are valid if they are not None
        standings[h]['GP'] += 1
        standings[a]['GP'] += 1
        standings[h]['GF'] += hs
        standings[h]['GA'] += ascore
        standings[a]['GF'] += ascore
        standings[a]['GA'] += hs

        if hs > ascore:
            standings[h]['W'] += 1; standings[h]['Pts'] += 3
            standings[a]['L'] += 1
        elif ascore > hs:
            standings[a]['W'] += 1; standings[a]['Pts'] += 3
            standings[h]['L'] += 1
        else:
            standings[h]['D'] += 1; standings[h_team]['Pts'] += 1
            standings[a]['D'] += 1; standings[a_team]['Pts'] += 1

    st_df = pd.DataFrame.from_dict(standings, orient='index')
    st_df['GD'] = st_df['GF'] - st_df['GA']
    return st_df.sort_values(by=['Pts', 'GD'], ascending=False)