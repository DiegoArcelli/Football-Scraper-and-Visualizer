import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from tqdm import tqdm
from utils import scatter_plot
import numpy as np
import os

def plot_double_line(gols, xg, title, x_label, y_label):
    x = [y+1 for y in range(len(goals))]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=gols,
                        mode='lines',
                        name='Goals'))
    fig.add_trace(go.Scatter(x=x, y=xg,
                        mode='lines',
                        name='xG'))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        # legend_title="Legend Title",
    )

    fig.show()


def plot_single_line(data, title, x_label, y_label):
    x = [y+1 for y in range(len(goals))]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=data,
                        mode='lines',
                        name='xG difference'))
    fig.add_hline(y=0.0)


    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        # legend_title="Legend Title",
    )

    fig.show()


def get_cumulative(vector):

    sum = 0
    cum_vector = []
    for i in range(len(vector)):
        sum += vector[i]
        cum_vector.append(sum)
    return np.array(cum_vector)



parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="", type=str)
parser.add_argument('--player_id', default="79443529", type=str)
parser.add_argument('--penalty', action="store_true")

args = parser.parse_args()

league = args.league
season = args.season
player_id = args.player_id
penalty = args.penalty

player_name = open(f"./../../datasets/shots/{player_id}/name", "r").read()


search_dir = f"./../../datasets/shots/{player_id}/"

if season == "":
    dir_seasons = [search_dir + d + "/"  for d in os.listdir(search_dir) if os.path.isdir(os.path.join(search_dir, d))]
else:
    dir_seasons = [search_dir + season + "/"]

if league == "":
    shots_files = [dir_season + f for dir_season in dir_seasons for f in os.listdir(dir_season) if os.path.isfile(os.path.join(dir_season, f))]
else:
    shots_files = [dir_season + league + ".csv" for dir_season in dir_seasons] + [dir_season + "minutes.csv" for dir_season in dir_seasons]
print(shots_files)

minutes_files = list(filter(lambda x: "minutes.csv" in x, shots_files))
shots_files = list(filter(lambda x: "minutes.csv" not in x, shots_files))

season_data_list = []
for minutes_file, shots_file in zip(minutes_files, shots_files):
    print(shots_files)
    minutes_data = pd.read_csv(minutes_file)
    shots_data = pd.read_csv(shots_file)
    season_data = pd.merge(shots_data, minutes_data, on='match_id', how='inner')
    season_data_list.append(season_data)

print(season_data_list)
shots_df = pd.concat(season_data_list)

if not penalty:
    shots_df = shots_df[shots_df["penalty"] == False]


games_df = shots_df.groupby("match_id").sum()

goals = games_df["scored"]
xg = games_df["xg"]
plot_double_line(
    goals,
    xg,
    f"{player_name} xG and goals per game",
    f"Games",
    f"Goals/xG",
)

cum_goals = get_cumulative(goals.tolist())
cum_xg = get_cumulative(xg.tolist())
plot_double_line(
    cum_goals,
    cum_xg,
    f"{player_name} cumulative xG and goals",
    f"Games",
    f"Goals/xG",    
)

xg_diff = goals-xg
plot_single_line(
    xg_diff,
    f"{player_name} xG difference per game",
    f"Games",
    f"xG difference", 
)


cum_xg_diff = cum_goals-cum_xg
plot_single_line(
    cum_xg_diff,
    f"{player_name} cumulative xG difference",
    f"Games",
    f"xG difference", 
)


