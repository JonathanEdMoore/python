import pandas as pd

# Load CSV
df = pd.read_csv("ncsrcp.csv")

# Function to append suffix based on competition
def tag_team(row):
    team_name = row['team']
    comp = row['competition']
    
    if "Women's" in comp:
        team_name += "_w"
    elif "NCAA" in comp and "baseball" in comp.lower():
        team_name += "_bb"
    
    return team_name

# Apply tagging
df['team'] = df.apply(tag_team, axis=1)

# Save updated CSV
df.to_csv("teams_tagged.csv", index=False)

print("Teams updated with '_w' and '_bb' suffixes and saved to 'teams_tagged.csv'")

