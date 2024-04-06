import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--minutes', default=200, type=int)
parser.add_argument('--npxg', default=1.0, type=float)
parser.add_argument('--all_comps', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
minutes = args.minutes
all_comps = args.all_comps
npxg = args.npxg

players_to_show = [
    "Kylian Mbappé",
    "Vinicius Júnior",
    "Lionel Messi",
    "Victor Osimhen",
    "Harry Kane",
    "Lautaro Martínez",
    "Erling Haaland",
    "Jude Bellingham",
    "Dušan Vlahović",
    "Victor Boniface"
]

data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"

data = pd.read_csv(data_path)
data = data[["player_id", "player", "minutes", "npxg_per90", "npxg_per_shot", "npxg"]]


if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[data["minutes"] > minutes]
data = data[data["npxg"] > npxg]

players = data["player"]

x_column = "npxg_per90"
y_column = "npxg_per_shot"
x_label = "np-xG per 90 minutes"
y_label = "np-xG per shot"
text = [f"{data['player'].iloc[i]}<br>np-xG p90: {round(data['npxg_per90'].iloc[i], 2)}<br>np-xG per shot: {round(data['npxg_per_shot'].iloc[i], 2)}" for i in range(len(players))]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="player",
    data_to_annotate=players_to_show,
    text=text,
    x_label=x_label,
    y_label=y_label,
    title=f'{x_label} {league if league != "" else "top 5 leagues"} {season} (players with at least {minutes} minutes played and {npxg} np-xG)',
    show_avg=True
)