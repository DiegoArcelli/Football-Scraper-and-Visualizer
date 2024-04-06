import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--threshold', default=500, type=int)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--p90', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
all_comps = args.all_comps
p90 = args.p90

players_to_show = [
    "Kylian Mbappé",
    "Vinicius Júnior",
    "Lionel Messi",
    "Harry Kane",
    "Jude Bellingham",
    "Khvicha Kvaratskhelia",
    "Rafael Leão",
    "Bukayo Saka",
    "Jamal Musiala",
    "Kevin De Bruyne",
    "Neymar"
]

data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"

data = pd.read_csv(data_path)

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[["player_id", "player", "pass_xa", "assists", "minutes"]]
data = data[data["minutes"] > threshold]
players = data["player"]

data["xa_net"] = data["assists"] - data["pass_xa"]
data["pass_xa_p90"] = (data["pass_xa"]/data["minutes"])*90

x_column = "xa_net"    
y_column = "pass_xa_p90" if p90 else "pass_xa_p90" 
x_label = "xA overperformance"
y_label = "xA per 90 minutes" if p90 else "xA"


text = [f"{data['player'].iloc[i]}<br>xA: {round(data['pass_xa'].iloc[i], 2)}<br>xA p90: {round(data['pass_xa_p90'].iloc[i], 2)}<br>xA over: {round(data['xa_net'].iloc[i], 2)}" for i in range(len(players))]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column=y_column,
    annotation_column="player",
    data_to_annotate=players_to_show,
    text=text,
    x_label=x_label,
    y_label=y_label,
    title=f'{x_label} {league if league != "" else "top 5 leagues"} {season} (players with at least {threshold} minutes)',
    show_avg=False
)