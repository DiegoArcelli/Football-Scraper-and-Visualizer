import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import argparse
import numpy as np
import matplotlib.pyplot as plt

def compute_percentile(data, value):
    data  = data.to_numpy()
    n = len(data)
    dat_mask = (data < value)
    s = dat_mask.sum()
    return s/n, n-s, n

def get_color(perc_color_map, perc):
    percentiles = list(perc_color_map.keys()) 
    n = len(percentiles)
    last = 0
    for i in range(n):
        if percentiles[i] >= perc:
            break
        else:
            last = percentiles[i]
    return perc_color_map[perc]



parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--threshold_stat', default="minutes", type=str)
parser.add_argument('--threshold', default=200, type=int)
parser.add_argument('--player_id', default='b0f7e36c', type=str)
parser.add_argument('--stats_name', default="take_ons_won", type=str)
parser.add_argument('--p90', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
threshold_stat = args.threshold_stat
all_comps = args.all_comps
p90 = args.p90
player_id = args.player_id
stats_name = args.stats_name

data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"

data = pd.read_csv(data_path)

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

# stats_name = "take_ons_won"

if p90:
    data[f"{stats_name}_p90"] = data[stats_name]/data["minutes"]*90
    stats_name = f"{stats_name}_p90"

player_data = data[data["player_id"] == player_id]
player_stats = player_data[stats_name].iloc[0]
player_name = player_data["player"].iloc[0]

data = data[data[threshold_stat] >= threshold]
stats_data = data[stats_name].fillna(0.0)

perc, rank, tot = compute_percentile(stats_data, player_stats)
print(rank, tot)
top = 1-perc

description = f"Player: {player_name}\n"\
                f"Player ID: {player_id}\n"\
                f"Stats: {stats_name}\n"\
                f"League: {league}\n"\
                f"Season: {season}\n"\
                f"All competitions: {all_comps}\n"\
                f"Stats value: {round(player_stats, 4)}\n"\
                f"Percentile: {round(perc*100, 4)}%\n"\
                f"Top: {round(top*100, 4)}%\n"\
                f"Rank: {rank}/{tot}"

print(description)

dist = ff.create_distplot([stats_data], [stats_name], bin_size=20, show_rug=False, show_hist=False).data[0]
# fig = px.area(x=dist.x, y=dist.y)    

x_data = list(dist.x)
y_data = list(dist.y)

mask = dist.x < player_stats
idx = sum(mask)

if player_stats not in x_data:
    if idx < len(x_data):
        avg_y = (y_data[idx-1] + y_data[idx])/2
    else:
        avg_y = y_data[idx-1]
    x_data = x_data[:idx] + [player_stats] + x_data[idx:]
    y_data = y_data[:idx] + [avg_y] + y_data[idx:]
    

n_colors = len(stats_data)
coolwarm_cmap = plt.get_cmap('coolwarm')
perc_colors = coolwarm_cmap(np.linspace(0, 1, n_colors))
perc_colors = [f"rgba{r,g,b,a}" for r,g,b,a in perc_colors]
perc_color_map = {i/n_colors: perc_colors[i] for i in range(n_colors)}

perc_data = [compute_percentile(stats_data, value)[0] for value in x_data]
colors = [get_color(perc_color_map, perc) for perc in perc_data]

fig = go.Figure()

n = len(x_data[:idx+1])-1
for i in range(0, n):
    fig.add_trace(go.Scatter(
            x=x_data[i:i+3],
            y=y_data[i:i+3],
            mode="lines",
            line_width=0,
            fill='tozeroy',
            line_color=colors[i],
            fillcolor=colors[i]
        )  
    )

fig.add_trace(go.Scatter(
        x=x_data[idx:],
        y=y_data[idx:],
        mode='lines',
        fill='tozeroy',
        line_color='grey',
        fillcolor='grey',
        line_width=0,
    )
)

# fig.update_yaxes(
#     scaleanchor="x",
#     scaleratio=1,
#   )

fig.add_vline(x=player_stats, line_width=1, line_dash="dash")

fig.add_trace( go.Scatter(
    x=[None],
    y=[None],
    mode='markers',
    marker=dict(
        colorscale=perc_colors, 
        showscale=True,
        cmin=-10,
        cmax=10,
        colorbar=dict(
            orientation='h',
            y=-0.15,
            thickness=20,
            tickvals=[-10, -5, 0, 5, 10],
            ticktext=['0.0', '0.25', '0.5', '0.75', '1.0']), 
    ),
    hoverinfo='none'
))

for trace in fig['data']: 
    trace['showlegend'] = False

fig.show()