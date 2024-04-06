import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from tqdm import tqdm
from utils import scatter_plot
import numpy as np
import os


def get_shots_list(data_dir):
    
    data = pd.read_csv(data_dir)
    shots_list = []

    for shot in data.itertuples():
        idx, match_id, minute, xg, xgot, scored, penalty = shot

        if penalty:
            continue

        shots_list.append((xg, xgot, scored))

    return shots_list


def get_bar_plot(x, first_player_data, second_player_data, first_player, second_player, title, x_label, y_label): 

    fig = go.Figure(
        data=[
            go.Bar(
                name=f"{first_player} shots",
                x=x,
                y=first_player_data["shots"],
                offsetgroup=0,
                marker=dict(color="#bd5b5b")
            ),
            go.Bar(
                name=f"{first_player} goals",
                x=x,
                y=first_player_data["goals"],
                offsetgroup=0,
                marker=dict(color="#990303"),
            ),
            go.Bar(
                name=f"{second_player} shots",
                x=x,
                y=second_player_data["shots"],
                offsetgroup=1,
                marker=dict(color="#707ce6"),
            ),
            go.Bar(
                name=f"{second_player} goals",
                x=x,
                y=second_player_data["goals"],
                offsetgroup=1,
                marker=dict(color="#001aff")
            ),
        ],
    )

    fig.update_layout(
        barmode='group',
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
    )

    fig.show()


def extract_xg(player_id, league):

    data_dir = f"./../../datasets/shots/{player_id}/" + f"{season + '/' if season != '' else ''}" + league + ".csv"

    shots_files = [f"./../../datasets/shots/{player_id}/" + f"{season + '/' if season != '' else ''}" + league + ".csv"]
    # shots_list = []
    # dir_elements = [element for element in  data_dir.split("/") if element != ""]

    # idx = dir_elements.index(player_id)

    # search_dir = "/".join(dir_elements[:idx+1]) +  "/"
    # if season == "":
    #     dir_seasons = [search_dir + d + "/"  for d in os.listdir(search_dir) if os.path.isdir(os.path.join(search_dir, d))]
    # else:
    #     dir_seasons = [search_dir + season + "/"]

    # if league == "":
    #     shots_files = []
    #     shots_files = [dir_season + f for dir_season in dir_seasons for f in os.listdir(dir_season) if os.path.isfile(os.path.join(dir_season, f))]
    # else:
    #     shots_files = [dir_season + league for dir_season in dir_seasons]

    shots_lists = [get_shots_list(shot_file) for shot_file in shots_files]
    shots_list = [shot for shots_list in shots_lists for shot in shots_list]

    # num_shots = len(shots_list)
    # goals_scored = sum(map(lambda shot: shot[2], shots_list))

    idx = 0 if stat == "xg" else 1
    shots = list(map(lambda shot: (shot[idx], True if shot[-1] == 1 else False), shots_list))
    return shots



parser = argparse.ArgumentParser(description='.')
parser.add_argument('--first_player_league', default="", type=str)
parser.add_argument('--second_player_league', default="", type=str)
parser.add_argument('--season', default="", type=str)
parser.add_argument('--first_player_id', default="79443529", type=str)
parser.add_argument('--second_player_id', default="f7036e1c", type=str)
parser.add_argument('--stat', default="xg", type=str)
parser.add_argument('--penalty', action="store_true")


args = parser.parse_args()

first_player_league = args.first_player_league
second_player_league = args.second_player_league
season = args.season
first_player_id = args.first_player_id
second_player_id = args.second_player_id 
penalty = args.penalty
stat = args.stat

first_player_name = open(f"./../../datasets/shots/{first_player_id}/name", "r").read()
second_player_name = open(f"./../../datasets/shots/{second_player_id}/name", "r").read()
stat_name = "xG" if stat == "xg" else "xGoT"

first_player_xgs = extract_xg(first_player_id, first_player_league)
second_player_xgs = extract_xg(second_player_id, second_player_league)

thresholds = [0] + [x/10 for x in range(1, 11)]

first_player_goals = []
second_player_goals = []
first_player_shots = []
second_player_shots = []

x_ticks = []
for i in range(len(thresholds)-1):
    lower = thresholds[i]
    upper = thresholds[i+1]
    first_player_shot = len(list(filter(lambda x: x[0] > lower and x[0] <= upper, first_player_xgs)))
    second_player_shot = len(list(filter(lambda x: x[0] > lower and x[0] <= upper, second_player_xgs)))
    first_player_shots.append(first_player_shot)
    second_player_shots.append(second_player_shot)

    first_player_goal = len(list(filter(lambda x: x[0] > lower and x[0] <= upper and x[1], first_player_xgs)))
    second_player_goal = len(list(filter(lambda x: x[0] > lower and x[0] <= upper and x[1], second_player_xgs)))

    first_player_goals.append(first_player_goal)
    second_player_goals.append(second_player_goal)
    x_ticks.append(f"{lower} - {upper}")

# if frequency:
#     first_sum = sum(first_player_counts)
#     second_sum = sum(second_player_counts)
#     first_player_counts = [x/first_sum for x in first_player_counts]
#     second_player_counts = [x/second_sum for x in second_player_counts]


first_player_dict = {
    "shots": first_player_shots,
    "goals": first_player_goals,
    "ranges": x_ticks
}

second_player_dict = {
    "shots": second_player_shots,
    "goals": second_player_goals,
    "ranges": x_ticks
}

first_player_data = pd.DataFrame(first_player_dict)
second_player_data = pd.DataFrame(second_player_dict)


print(first_player_data)
print(second_player_data)
# print(second_player_goals)

get_bar_plot(
    x_ticks,
    first_player_data,
    second_player_data,
    first_player_name,
    second_player_name,
    f"{first_player_name} ({sum(first_player_goals)} goals) vs {second_player_name} ({sum(second_player_goals)} goals)",
    "xG intevals",
    "Number of occasions"
)