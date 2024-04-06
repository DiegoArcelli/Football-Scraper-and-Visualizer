import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--normalize', action="store_true")
parser.add_argument('--threshold', default=500, type=int)
parser.add_argument('--all_comps', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
normalize = args.normalize
all_comps = args.all_comps


player_data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"
gk_data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/goalkeepers.csv"


gk_to_show = [
    "Mike Maignan",
    "André Onana",
    "Wojciech Szczęsny",
    "Gianluigi Donnarumma"
]

gk_data = pd.read_csv(gk_data_path)
player_data = pd.read_csv(player_data_path)

data = pd.merge(gk_data, player_data, on="player_id", how='inner', suffixes=('', '_to_drop'))
data = data[[col for col in data.columns if not col.endswith("_to_drop")]]


data = data[["player_id", "player", "minutes", "gk_psxg_net", "gk_psxg", "gk_psnpxg_per_shot_on_target_against"]]

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")
data = data[data["minutes"] > threshold]

# takes_on_stats.replace(to_replace=None, value=0)
shot_quality = data["gk_psnpxg_per_shot_on_target_against"]
saved_goals = data["gk_psxg_net"]
xgot = data["gk_psxg"]
players = data["player"]
minutes = data["minutes"]

gk_performance = saved_goals
if normalize:
    gk_performance = saved_goals/xgot

data["gk_performance"] = gk_performance


text = [f"{players.iloc[i]}<br>Minutes: {minutes.iloc[i]}<br>Saved goals: {round(gk_performance.iloc[i], 2)}<br>Avg. shot quality: {shot_quality.iloc[i]}" for i in range(len(players))]

scatter_plot(
    data=data,
    x_column="gk_performance",
    y_column="gk_psnpxg_per_shot_on_target_against",
    annotation_column="player",
    data_to_annotate=gk_to_show,
    text=text,
    x_label='(xGoT - GA)/xGoT' if normalize else "xGoT - GA",
    y_label='Average shot quality faced',
    title=f'Goalkeepers performance {league if league != "" else "top 5 leagues"} {season} (goalkeepers with at least {threshold} minutes played)',
    show_avg=True
)