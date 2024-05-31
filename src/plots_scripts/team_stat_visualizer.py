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
    x = [y+1 for y in range(len(data))]

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
    x = [y+1 for y in range(len(data))]

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


def plot_lines(data_1, data_2, title, x_label, y_label):

    mean_1 = data_1.mean()
    mean_2 = data_2[1:].mean()
    print(mean_1, mean_2)

    x_1 = [y+1 for y in range(len(data_1))]
    m = max(x_1)
    x_2 = [m+y for y in range(len(data_2))]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_1, y=data_1,
                        mode='lines',
                        line=dict(color='Blue',),
                        name='First half data'))
    fig.add_trace(go.Scatter(x=x_2, y=data_2,
                        mode='lines',
                        line=dict(color='Red',),
                        name='Second half data'))

    fig.add_shape(
        type='line',
        x0=min(x_1),
        y0=mean_1,
        x1=max(x_1),
        y1=mean_1,
        line=dict(color='Blue',),
        xref='x',
        yref='y',
        name='First half average'
    )

    fig.add_shape(
        type='line',
        x0=min(x_2),
        y0=mean_2,
        x1=max(x_2),
        y1=mean_2,
        line=dict(color='Red',),
        xref='x',
        yref='y',
        name='Second half average'
    )   

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
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--team', default="Juventus", type=str)
parser.add_argument('--stat', default="npxg", type=str)
parser.add_argument('--opponent', action="store_true")



args = parser.parse_args()

data_path = f"./../../datasets/{args.season}/{args.league}/{args.team}/matchlogs/"

data_files = [d for d in os.listdir(data_path)]
data_files.sort(key=lambda x: int(x.split("_")[-1]))
team_files = [f"{data_path}{d}/team_stats.csv" for d in data_files]
opponent_files = [f"{data_path}{d}/opponent_stats.csv" for d in data_files]

team_dfs = [pd.read_csv(f) for f in team_files]
opponent_dfs = [pd.read_csv(f) for f in opponent_files]

team_df = pd.concat(team_dfs).reset_index()
opponent_df = pd.concat(opponent_dfs).reset_index()
# team_df["match_id"] = [x for x in range(len(team_df))]
# opponent_df["match_id"] = [x for x in range(len(team_df))]

data = opponent_df if args.opponent else team_df
data.drop(data.tail(2).index, inplace = True)

goals = data["goals"]
xg_agg = opponent_df["xg"]
xg = data["xg"]
npxg = data["npxg"]
shots = data["shots"]
series = goals-xg
series = npxg/shots
series = xg-xg_agg
# series = data[args.stat]

split = 22
series_1 = series[:split+1]
series_2 = series[split:]


# plot_single_line(stat, args.stat, "Match ID", args.stat)
plot_lines(series_1, series_2, args.stat, "Match ID", args.stat)