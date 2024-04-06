import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)

args = parser.parse_args()

season = args.season
league = args.league


teamsto_show = [
    "Milan",
    "Juventus",
    "Inter",
    "Lazio",
    "Roma",
    "Atalanta",
    "Napoli",
    "Fiorentina",
    "Leverkusen",
    "Barcellona",
    "Bayern Munich",
    "Girona",
    "Atletico Madrid",
    "Dortmund",
    "Chelsea",
    "Manchester City",
    "Barcelona",
    "Stuttgart",
    "Liverpool",
    "Brighton",
    "Aston Villa",
    "Arsenal",
    "Totthenam",
    "Newcastle Utd" 
]



if league != "":
    team_data_path = f"./../../datasets/{season}/{league}/team.csv"
    opp_data_path = f"./../../datasets/{season}/{league}/opponents.csv"
else:
    team_data_path = f"./../../datasets/{season}/team.csv"
    opp_data_path = f"./../../datasets/{season}/opponents.csv"

data = pd.read_csv(team_data_path)
data = data[["team", "npxg_per90", "xg_per90", "npxg_per_shot"]]


x_column = "npxg_per90"
y_column = "npxg_per_shot"

npxg = data[x_column]
npxg_per_shot = data[y_column]

teams = data["team"]

text = [f"{teams.iloc[i]}<br>np-xG p90: {round(npxg.iloc[i], 2)}<br>np-xG per shot p90: {round(npxg_per_shot.iloc[i], 2)}" for i in range(len(teams))]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="team",
    data_to_annotate=teamsto_show,
    text=text,
    x_label='np-xG per 90 minutes',
    y_label='np-xG per shot',
    title=f'Offensive performance {league if league != "" else "top 5 leagues"} {season}',
)