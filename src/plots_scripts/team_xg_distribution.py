import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse
from tqdm import tqdm
from utils import scatter_plot
import numpy as np
import os
from functools import reduce

def get_shots_list(shot_file, team):
    data = pd.read_csv(shot_file)
    shots_list = []

    for shot in data.itertuples():

        if shot.team_name != team or shot.penalty:
            continue

        shots_list.append((shot.xg, shot.xgot, shot.scored))

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
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2024-2025", type=str)
parser.add_argument('--team', default="Milan", type=str)
parser.add_argument('--penalty', action="store_true")
parser.add_argument('--iters', default=10000, type=int)
parser.add_argument('--stat', default="xg", type=str)

args = parser.parse_args()

league = args.league
season = args.season
team = args.team
penalty = args.penalty
stat = args.stat
iters = args.iters

matches_dir_path = f"./../../datasets/{season}/{league}/matches/"
stat_name = "xG" if stat == "xg" else "xGoT"

team_matches = [match for match in os.listdir(matches_dir_path) if team in match]

team_matches_shot_files = [f"{matches_dir_path}{match}/shots.csv" for match in team_matches]

matches_shots = [get_shots_list(shots_file, team) for shots_file in team_matches_shot_files]


shots_list = reduce(lambda matches, match: [*matches, *match], matches_shots, [])
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
{team} {stat_name} simulation {league} {season} ({iters} simulations)<br>
Probability of scoring {goals_scored} goals: {equal}<br>
Probability of scoring more than {goals_scored} goals: {more}<br>
Probability of scoring more or equal then {goals_scored} goals: {more_or_equal}<br>
Probability of scoring less then {goals_scored} goals: {less}<br>
Probability of scoring less or equal then {goals_scored} goals: {less_or_equal}"""


title = f"""{team} {stat_name} simulation {league} {season} ({iters} simulations)<br>
Probability of scoring more than {goals_scored} goals: {more}<br>
Probability of scoring less then {goals_scored} goals: {less}<br>"""

get_bar_plot(prob_dict.keys(), prob_dict.values(),  title, "Goals", "Probability", goals_scored)