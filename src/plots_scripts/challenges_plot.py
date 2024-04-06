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
parser.add_argument('--p90', action="store_true")
parser.add_argument('--all_comps', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
p90 = args.p90
all_comps = args.all_comps


players_to_show = [
    "Alessandro Bastoni",
    "Davide Calabria",
    "Kim Min-jae",
    "Danilo",
    "Bryan Cristante",
    "William Saliba",
    "Matthijs de Ligt",
    "Dayot Upamecano",
    "Virgil van Dijk",
    "Rúben Dias",
    "John Stones",
]

data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"


data = pd.read_csv(data_path)

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[["player_id", "player", "minutes", "challenges", "challenge_tackles", "challenge_tackles_pct"]]
data = data[data["challenges"] > threshold]
data["challenge_tackles_p90"] = (data["challenge_tackles"]/data["minutes"])*90


x_column = "challenge_tackles"

if p90:
    x_column = "challenge_tackles_p90"

players = data["player"]


text = [
    f"{data['player'].iloc[i]}<br>Challanges faced: {round(data['challenges'].iloc[i], 2)}<br>Challanges won: {round(data['challenge_tackles'].iloc[i], 2)}<br>Challanges won p90: {round(data['challenge_tackles_p90'].iloc[i], 2)}<br>Challenges won pct: {round(data['challenge_tackles_pct'].iloc[i], 2)}<br>"
    for i in range(len(players))
]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column="challenge_tackles_pct",
    annotation_column="player",
    data_to_annotate=players_to_show,
    text=text,
    x_label=f"Challenges won {'per 90 minutes' if p90 else ''}",
    y_label='Challenges won percentage',
    title=f'Challenges {league if league != "" else "top 5 leagues"} {season} (players with at least {threshold} tackles attempted)',
    show_avg=True
)