import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)

args = parser.parse_args()

league = args.league


teamsto_show = [
    "Milan",
    "Juventus",
    "Internazionale",
    "Lazio",
    "Roma",
    "Atalanta",
    "Napoli",
    "Fiorentina",
    "Bayer 04 Leverkusen",
    "Barcellona",
    "FC Bayern München",
    "Girona",
    "Atlético de Madrid",
    "Borussia Dortmund",
    "Chelsea",
    "Manchester City",
    "Barcelona",
    "VfB Stuttgart",
    "Liverpool",
    "Paris Saint-Germain",
    "Aston Villa",
    "Arsenal",
    "Real Madrid",
    "Newcastle United",
    "RB Leipzig",
    "Marseille",
    "Tottenham Hotspur",
    "Brighton and Hove Albion",
    "Brentford"
]

attotation_pos = {
    "Barcelona": (-10, 30),
    "Manchester City": (75, 0),
    "Girona": (10, 30),
    "Roma": (-20, 30),
    "Real Madrid": (20, 30),
    "Bayer 04 Leverkusen": (10, 30),
    "Internazionale": (30, -30),
    "Tottenham Hotspur": (-30, 40),
    "Chelsea": (10, -30),
    "Brighton and Hove Albion": (-100, 0),
    "RB Leipzig": (-30, 30),
    "Juventus": (30, 40),
    "Borussia Dortmund": (-30, -30),
    "Newcastle United": (10, -30),
    "Paris Saint-Germain": (0, -30),
}



if league != "":
    team_data_path = f"./../../datasets/TheAnalyst/{league}.csv"
else:
    team_data_path = f"./../../datasets/TheAnalyst/All-Competitions.csv"

data = pd.read_csv(team_data_path)
data = data[["team", "open_play_shots", "open_play_xg", "minutes"]]

data["open_play_xg_p90"] = data["open_play_xg"]/data["minutes"]*90
data["open_play_xg_per_shot"] = data["open_play_xg"]/data["open_play_shots"]

x_column = "open_play_xg_p90"
y_column = "open_play_xg_per_shot"

npxg = data[x_column]
npxg_per_shot = data[y_column]

teams = data["team"]

text = [f"{teams.iloc[i]}<br>Open play shots p90: {round(npxg.iloc[i], 2)}<br>Open play shots xG per shot p90: {round(npxg_per_shot.iloc[i], 2)}" for i in range(len(teams))]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="team",
    data_to_annotate=teamsto_show,
    text=text,
    x_label='Open play shots xG per 90 minutes',
    y_label='xG per open play shot',
    title=f'Open play shots xG performance {league if league != "" else "top 5 leagues"} 2023-2024',
    images=False,
    annotation_position=attotation_pos
)