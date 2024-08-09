import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
import sys
sys.path.append("./../")
from utils import *

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--threshold_minutes', default=200, type=int)
parser.add_argument('--threshold_take_ons', default=5, type=int)
parser.add_argument('--all_comps', action="store_true")

args = parser.parse_args()

season = args.season
league = args.league
threshold_minutes = args.threshold_minutes
threshold_take_ons = args.threshold_take_ons
all_comps = args.all_comps


players_to_show = [
    "Khvicha Kvaratskhelia",
    "Rafael Leão",
    "Matìas Soulé",
    # "Zito",
    "Kylian Mbappé",
    "Jeremy Doku",
    "Leroy Sané",
    "Vinicius Júnior",
    "Kenan Yıldız",
    # # "Gabriel Martinelli",
    # "Bukayo Saka",
    "Jamal Musiala",
    # # "Jude Bellingham",
    # "Lionel Messi",
    # "Neymar"
]


# if league != "":
#     data_path = f"./../../datasets/{season}/{league}/players.csv"
# else:
#     data_path = f"./../../datasets/{season}/players.csv"

data_path = f"./../../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"

print(data_path)

data = pd.read_csv(data_path)
data = data[["nationality", "player_id", "player", "minutes", "take_ons_won", "take_ons_won_pct", "touches"]]

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[data["minutes"] >= threshold_minutes]
data = data[data["take_ons_won"] >= threshold_take_ons]
data = data[data["nationality"] == "eng ENG"]

# takes_on_stats.replace(to_replace=None, value=0)
take_ons_won = data["take_ons_won"]
take_ons_succ = data["take_ons_won_pct"]
touches = data["touches"]
players = data["player"]
minutes = data["minutes"]


data["take_ons_won_per_90"] = (take_ons_won/minutes)*90
take_ons_won_per_90 = data["take_ons_won_per_90"]


x_column = "take_ons_won_per_90"

text = [f"{players.iloc[i]}<br>Succ. Dribblings: {round(take_ons_won.iloc[i], 2)}<br>Succ. Dribblings per 90': {round(take_ons_won_per_90.iloc[i], 2)}<br>Dribbling Succ. Rate: {take_ons_succ.iloc[i]}" for i in range(len(players))]

scatter_plot(
    data=data,
    x_column=x_column,
    y_column="take_ons_won_pct",
    annotation_column="player",
    data_to_annotate=players_to_show,
    text=text,
    x_label=f'Number of successful driblings per 90 minutes',
    y_label='Successful dribbling percentage',
    title=f'Dribbling quality {league if league != "" else "top 5 leagues"} {season} (players with at least {threshold_minutes} minutes played and {threshold_take_ons} dribblings attempted)',
)
