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


def get_bar_plot(x, y,  title, x_label, y_label, to_color): 

    x = list(x)
    y = list(y)

    colors = ["#636EFA" if val != to_color else "#EF553B" for val in x]

    fig = go.Figure(
        data=[
            go.Bar(
                x=x,
                y=y,
                marker_color=colors,
            )
        ],
    )

    fig.update_layout(
        title=title,
        xaxis=dict(title=x_label),
        yaxis=dict(title=y_label),
    )

    fig.show()



parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="", type=str)
parser.add_argument('--player_id', default="79443529", type=str)
parser.add_argument('--penalty', action="store_true")
parser.add_argument('--iters', default=10000, type=int)
parser.add_argument('--stat', default="xg", type=str)

args = parser.parse_args()

league = args.league
season = args.season
player_id = args.player_id
penalty = args.penalty
stat = args.stat
iters = args.iters

player_name = open(f"./../../datasets/shots/{player_id}/name", "r").read()
stat_name = "xG" if stat == "xg" else "xGoT"


data_dir = f"./../../datasets/shots/{player_id}/" + f"{season + '/' if season != '' else ''}" + f"{league}.csv"
print(data_dir)


shots_list = []
dir_elements = [element for element in  data_dir.split("/") if element != ""]

idx = dir_elements.index(player_id)

search_dir = "/".join(dir_elements[:idx+1]) +  "/"
if season == "":
    dir_seasons = [search_dir + d + "/"  for d in os.listdir(search_dir) if os.path.isdir(os.path.join(search_dir, d))]
else:
    dir_seasons = [search_dir + season + "/"]

if league == "":
    shots_files = []
    shots_files = [dir_season + f for dir_season in dir_seasons for f in os.listdir(dir_season) if os.path.isfile(os.path.join(dir_season, f))]
else:
    shots_files = [dir_season + league for dir_season in dir_seasons]

shots_files = list(filter(lambda x: "minutes.csv" not in x, shots_files))

shots_lists = [get_shots_list(shot_file) for shot_file in shots_files]
shots_list = [shot for shots_list in shots_lists for shot in shots_list]

num_shots = len(shots_list)
goals_scored = sum(map(lambda shot: shot[2], shots_list))

idx = 0 if stat == "xg" else 1
shots = list(map(lambda shot: shot[idx], shots_list))

prob_dict = {}

with tqdm(total=iters) as pbar:
    for iter in range(iters):
        goals = sum([np.random.binomial(1, xg, 1)[0] for xg in shots])
        if goals in prob_dict.keys():
            prob_dict[goals] += 1
        else:
            prob_dict[goals] = 1

        pbar.update(1)

for key in prob_dict.keys():
    prob_dict[key] /= iters

equal = prob_dict[goals_scored]
more, less = 0, 0
for key in prob_dict.keys():
    if key > goals_scored:
        more += prob_dict[key]
    if key < goals_scored:
        less += prob_dict[key]
more_or_equal, less_or_equal = more + equal, less + equal

title = f"""
{player_name} {stat_name} simulation {league} {season} ({iters} simulations)<br>
Probability of scoring {goals_scored} goals: {equal}<br>
Probability of scoring more than {goals_scored} goals: {more}<br>
Probability of scoring more or equal then {goals_scored} goals: {more_or_equal}<br>
Probability of scoring less then {goals_scored} goals: {less}<br>
Probability of scoring less or equal then {goals_scored} goals: {less_or_equal}"""


title = f"""{player_name} {stat_name} simulation {league} {season} ({iters} simulations)<br>
Probability of scoring more than {goals_scored} goals: {more}<br>
Probability of scoring less then {goals_scored} goals: {less}<br>"""

get_bar_plot(prob_dict.keys(), prob_dict.values(),  title, "Goals", "Probability", goals_scored)
