import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--threshold', default=200, type=int)
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
data = data[["player_id", "player", "minutes", "goals_pens", "goals_pens_per90", "goals", "goals_per90", "xg_net", "npxg_net"]]


if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[data["goals"] > 1]
data = data[data["minutes"] > threshold]
players = data["player"]

data["xg_net_per90"] = (data["xg_net"]/data["minutes"])*90
data["npxg_net_per90"] = (data["npxg_net"]/data["minutes"])*90

if penalty:
    x_column = "goals_per90" if p90 else "goals"
    y_column = "xg_net_per90" if p90 else "xg_net" 
    x_label = "Goals per 90 minutes" if p90 else "Goals"
    y_label = "xG overperformance per 90 minutes" if p90 else "xG overperformance"
    text = [f"{data['player'].iloc[i]}<br>Goals: {round(data['goals'].iloc[i], 2)}<br>Goals p90: {round(data['goals_per90'].iloc[i], 2)}<br>xG over: {round(data['xg_net'].iloc[i], 2)}<br>xG over p90: {round(data['xg_net_per90'].iloc[i], 2)}" for i in range(len(players))]
else:
    x_column = "goals_pens_per90" if p90 else "goals_pens"
    y_column = "npxg_net_per90" if p90 else "npxg_net" 
    x_label = "Non penalty goals per 90 minutes" if p90 else "Non penalty"
    y_label = "xG overperformance per 90 minutes" if p90 else "xG overperformance"
    text = [f"{data['player'].iloc[i]}<br>np-Goals: {round(data['goals'].iloc[i], 2)}<br>np-Goals p90: {round(data['goals_per90'].iloc[i], 2)}<br>np-xG over: {round(data['npxg_net'].iloc[i], 2)}<br>np-xG over p90: {round(data['npxg_net_per90'].iloc[i], 2)}" for i in range(len(players))]


scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="player",
    data_to_annotate=players_to_show,
    text=text,
    x_label=x_label,
    y_label=y_label,
    title=f'{x_label} {league if league != "" else "top 5 leagues"} {season} (players with at least {threshold} minutes played)',
    show_avg=False
)