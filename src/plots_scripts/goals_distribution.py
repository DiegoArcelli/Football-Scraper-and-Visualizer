import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
import os

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--stat', default="goals", type=str)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--perc', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
all_comps = args.all_comps
stat = args.stat
perc = args.perc

base_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}"
teams = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

datasets = []
for team in teams:
    team_path = f"{base_path}/{team}/players.csv"
    team_data = pd.read_csv(team_path)
    team_data = team_data[["position", stat, "player"]]
    positions = team_data["position"]
    team_data["position"] = pd.Series([ pos if len(pos.split(",")) == 1 else pos.split(",")[0]  for pos in positions])
    goals_per_pos = team_data.groupby("position", as_index=False).sum()
    goals_per_pos["team"] = team
    goals_per_pos.loc[0], goals_per_pos.loc[1], goals_per_pos.loc[2], goals_per_pos.loc[3] = goals_per_pos.loc[2].copy(), goals_per_pos.loc[0].copy(), goals_per_pos.loc[3].copy(), goals_per_pos.loc[1].copy()

    if perc:
        stat_sum = sum(goals_per_pos[stat])
        goals_per_pos[stat] = goals_per_pos[stat]/stat_sum

    datasets.append(goals_per_pos)

data = pd.concat(datasets, ignore_index=True)

fig = px.bar(data, x="team", y=stat, color="position", title=f"{stat} distribution per team in {league} {season}")
fig.show()