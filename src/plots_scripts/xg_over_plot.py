import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--threshold', default=10, type=int)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--penalty', action="store_true")
parser.add_argument('--p90', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
penalty = args.penalty
all_comps = args.all_comps
p90 = args.p90

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
data = data[["player_id", "player", "shots", "npxg_net", "npxg", "xg", "xg_net", "minutes"]]
data = data[data["shots"] > threshold]
players = data["player"]

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data["xg_p90"] = (data["xg"]/data["minutes"])*90
data["npxg_p90"] = (data["npxg"]/data["minutes"])*90

if penalty:
    x_column = "xg_net"
    y_column = "xg_p90" if p90 else "xg" 
    x_label = "xG overperformance"
    y_label = "xG per 90 minutes" if p90 else "xG"
    text = [f"{data['player'].iloc[i]}<br>xG: {round(data['xg'].iloc[i], 2)}<br>xG p90: {round(data['xg_p90'].iloc[i], 2)}<br>xG over: {round(data['xg_net'].iloc[i], 2)}" for i in range(len(players))]
else:
    x_column = "npxg_net"
    y_column = "npxg_p90" if p90 else "npxg"
    x_label = "np-xG overperformance"
    y_label = "np-xG per 90 minutes" if p90 else "np-xG"
    text = [f"{data['player'].iloc[i]}<br>np-xG: {round(data['npxg'].iloc[i], 2)}<br>np-xG p90: {round(data['npxg_p90'].iloc[i], 2)}<br>np-xG over: {round(data['npxg_net'].iloc[i], 2)}" for i in range(len(players))]


scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="player",
    data_to_annotate=players_to_show,
    text=text,
    x_label=x_label,
    y_label=y_label,
    title=f'{x_label} {league if league != "" else "top 5 leagues"} {season} (players with at least {threshold} shots attempted)',
    show_avg=False
)