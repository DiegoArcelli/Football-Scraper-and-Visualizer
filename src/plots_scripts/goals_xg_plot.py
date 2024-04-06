import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--threshold', default=4, type=int)
parser.add_argument('--p90', action="store_true")
parser.add_argument('--penalty', action="store_true")
parser.add_argument('--all_comps', action="store_true")

args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
p90 = args.p90
all_comps = args.all_comps
penalty = args.penalty

players_to_show = [
    "Khvicha Kvaratskhelia",
    "Rafael Leão",
    "Dušan Vlahović",
    "Ciro Immobile",
    "Victor Osimhen",
    "Lautaro Martínez"
]


# if league != "":
#     data_path = f"./../../datasets/{season}/{league}/players.csv"
# else:
#     data_path = f"./../../datasets/{season}/players.csv"

data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"

print(data_path)

data = pd.read_csv(data_path)
data = data[["player_id", "player", "goals_pens_per90", "goals_pens", "npxg_per90", "xg_per90", "xg", "npxg", "goals", "goals_per90"]]
data = data[data["goals"] > threshold]
players = players = data["player"]


x_column = f"goals{'' if penalty else '_pens'}{'_per90' if p90 else ''}"
y_column = f"{'' if penalty else 'np'}xg{'_per90' if p90 else ''}"

x_label = f"{'Goals' if penalty else 'Non penalty goals'}{' per 90 minutes' if penalty else ''}"
y_label = f"{'xG' if penalty else 'np-xG'}{' per 90 minutes' if penalty else ''}"


text = [f'{players.iloc[i]}<br>Goals: {round(data["goals"].iloc[i], 2)}<br>Non penalty goals: {round(data["goals_pens"].iloc[i], 2)}<br>xG: {round(data["xg"].iloc[i], 2)}<br>np-xG: {round(data["npxg"].iloc[i], 2)}<br>Goals: {round(data["goals_per90"].iloc[i], 2)}<br>Non penalty goals: {round(data["goals_pens_per90"].iloc[i], 2)}<br>xG: {round(data["xg_per90"].iloc[i], 2)}<br>np-xG: {round(data["npxg_per90"].iloc[i], 2)}' for i in range(len(players))]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="player",
    data_to_annotate=players_to_show,
    text=text,
    x_label=x_label,
    y_label=y_label,
    title=f'Goals vs xGoals {league if league != "" else "top 5 leagues"} {season} (players with at least {threshold} goals scored)',
)