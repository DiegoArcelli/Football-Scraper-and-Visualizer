import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--penalty', action="store_true")

args = parser.parse_args()

season = args.season
league = args.league
penalty = args.penalty


teamsto_show = [
    "Milan",
    "Juventus",
    "Inter",
    "Lazio",
    "Roma",
    "Atalanta",
    "Napoli",
    "Fiorentina"
]

if league != "":
    team_data_path = f"./../../datasets/{season}/{league}/team.csv"
    opp_data_path = f"./../../datasets/{season}/{league}/opponents.csv"
else:
    team_data_path = f"./../../datasets/{season}/team.csv"
    opp_data_path = f"./../../datasets/{season}/opponents.csv"

team_data = pd.read_csv(team_data_path)
team_data = team_data[["team", "npxg_net", "xg_net"]]

opp_data = pd.read_csv(opp_data_path)
opp_data = opp_data[["team", "npxg_net", "xg_net"]]

data = pd.merge(team_data, opp_data, on="team", how='inner', suffixes=('_team', '_opponent'))
print(data)

if penalty:
    x_column = "xg_net_team"
    y_column = "xg_net_opponent"
else:
    x_column = "npxg_net_team"
    y_column = "npxg_net_opponent"

xg_over_team = data[x_column]
xg_over_opponent = data[y_column]

teams = data["team"]

text = [f"{teams.iloc[i]}<br>Team np-xG over: {round(xg_over_team.iloc[i], 2)}<br>Opp. np-xG over: {round(xg_over_opponent.iloc[i], 2)}" for i in range(len(teams))]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="team",
    data_to_annotate=teamsto_show,
    text=text,
    x_label='Team np-G - np-xG',
    y_label='Opponents np-G - np-xG',
    title=f'np-xG overperformance {league if league != "" else "top 5 leagues"} {season}',
)