import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from utils import scatter_plot

def get_stat(data, stat_name, games):
    stat_data = data[stat_name]
    return stat_data.sum()/games

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--cum', action="store_true")

args = parser.parse_args()

season = args.season
cum = args.cum

base_dir = f"./../../datasets/{season}"
serie_a_data = pd.read_csv(f"{base_dir}/Serie-A/team.csv")
premier_league_data = pd.read_csv(f"{base_dir}/Premier-League/team.csv")
la_liga_data = pd.read_csv(f"{base_dir}/La-Liga/team.csv")
bundesliga_data = pd.read_csv(f"{base_dir}/Bundesliga/team.csv")
ligue_1_data = pd.read_csv(f"{base_dir}/Ligue-1/team.csv")


serie_a_games = 1 if cum else serie_a_data["games"].sum()/2
premier_league_games = 1 if cum else premier_league_data["games"].sum()/2
la_liga_games = 1 if cum else la_liga_data["games"].sum()/2
bundesliga_games = 1 if cum else bundesliga_data["games"].sum()/2
ligue_1_games = 1 if cum else ligue_1_data["games"].sum()/2

stats = [
    ("goals", "Goals"),
    ("goals_pens", "np-Goals"),
    ("xg", "xG"),
    ("npxg", "np-xG"),
    ("shots", "Shots"),
    ("shots_on_target", "Shots on target"),
    ("pass_xa", "xA"),
    ("xg_net", "Goals - xG"),
    ("take_ons_won", "Succeded dribblings"),
    ("take_ons", "Attempted dribblings"),
    ("touches_att_3rd", "Touches in the attacking 3rd"),
    ("fouls", "Fouls"),
    ("passes", "Attempted passes"),
    ("passes_completed", "Compteded passes"),
    ("crosses", "Crosses")
]

for stat, stat_name in stats:

    data = {
        "Serie A": get_stat(serie_a_data, stat, serie_a_games),
        "Premier League": get_stat(premier_league_data, stat, premier_league_games),
        "La Liga": get_stat(la_liga_data, stat, la_liga_games),
        "Bundesliga": get_stat(bundesliga_data, stat, bundesliga_games),
        "Ligue 1": get_stat(ligue_1_data, stat, ligue_1_games)
    }
    data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

    print(f"{stat_name}:")
    for idx, (league, stat_value) in enumerate(data.items()):
        print(f"{idx+1}) {league}: {stat_value}")
    print("\n")