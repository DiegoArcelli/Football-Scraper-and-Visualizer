
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import re
from sklearn.decomposition import PCA
from plots_util import scatter_plot, radar_plot, parallel_coordinates, get_bar_plots_grid
from pandas.io.formats.style_render import DataFrame
from tqdm import tqdm
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn import metrics
from math import ceil
import argparse



def get_count_dict(data):
    counts = {}
    for x in data:
        counts[x] = 1 if x not in counts.keys() else counts[x] + 1
    return counts
           


parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--threshold', default=200, type=int)
parser.add_argument('--p90', action="store_true")
parser.add_argument('--k', default=2, type=int)

args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
all_comps = args.all_comps
k = args.k
p90 = args.p90

data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"

data = pd.read_csv(data_path)

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[data["minutes"] > threshold]

players = data["player"]

kmeans = KMeans(n_clusters=k, n_init=10, max_iter=100)

attributes = [
   "goals", "xg", "npxg", "xg_assist", "progressive_carries", "progressive_passes", "shots", "shots_on_target",
   "passes_short", "passes_completed_short", "passes_medium", "passes_completed_medium", "passes_long", "passes_completed_long",
   "passes_pct_short", "passes_pct_medium", "passes_pct_long", "pass_xa", "assisted_shots", "passes_into_final_third",
   "passes_into_penalty_area", "crosses_into_penalty_area", "crosses", "through_balls", "passes_switches", "sca", "gca",
   "tackles_won", "tackles", "tackles_def_3rd", "tackles_att_3rd", "tackles_mid_3rd", "challenge_tackles_pct", "challenges_lost",
   "blocks", "interceptions", "tackles_interceptions", "clearances", "errors", "touches", "touches_def_3rd", "touches_mid_3rd",
   "touches_att_3rd", "touches_att_pen_area", "take_ons", "take_ons_won", "take_ons_won_pct", "carries_into_final_third",
   "carries_into_penalty_area", "miscontrols", "progressive_passes_received", "fouls", "fouled", "ball_recoveries", "aerials_won",
   "aerials_won_pct"
]

if p90:
   for attribute in attributes:
      p90_attribute = (data[attribute]/data["minutes"])*90
      data[attribute] = p90_attribute

cluster_data = data[attributes]

cluster_data = cluster_data.fillna(0)

method = "standard"
if method == "minmax":
  scaler = MinMaxScaler()
elif method == "standard":
  scaler = StandardScaler()

X = scaler.fit_transform(cluster_data.values)
kmeans.fit(X)
sse = kmeans.inertia_
labels = kmeans.labels_
centers = kmeans.cluster_centers_

pca = PCA(n_components=2)

X_pca = pca.fit_transform(X)
X_pca.shape


unique_colors = plt.cm.jet(np.linspace(0,1,len(set(labels))))
unique_colors = (unique_colors*255).astype(np.uint8)
unique_colors = ['#%02x%02x%02x' % tuple(color[:-1]) for color in unique_colors.tolist()]


colors = [unique_colors[label] for label in labels]

# for label in set(labels):
#   mask = labels == label
#   x = X_pca[mask, 0]
#   y = X_pca[mask, 1]
#   color = labels[labels == label]

# print(X_pca.shape)



reduced_data = {
   "player": players.tolist(),
   "cluster": labels,
   "PCA 1": X_pca[:, 0].tolist(),
   "PCA 2": X_pca[:, 1].tolist()
}

reduced_data = pd.DataFrame.from_dict(reduced_data)
print(reduced_data)

text = [f"{players.iloc[i]}<br>Cluster: {labels[i]}" for i in range(len(players))]

scatter_plot(
    reduced_data,
    "PCA 1",
    "PCA 2",
    text,
    "player",
    [],
    "Visualize clusters in 2D",
    "PCA 1",
    "PCA 2",
    show_avg=False,
    annotation_position=None,
    colors=colors
)

data["cluster"] = labels


# positions = set(data["position"].tolist())

positions_data = []
for label in set(labels):
   label_data = data[data["cluster"] == label]
   label_position = label_data["position"].tolist()
   position_counts = get_count_dict(label_position)
   roles = list(position_counts.keys())
   counts = list(position_counts.values())
   positions_data.append((roles, counts))



get_bar_plots_grid(positions_data, num_clusters=k)

# print(positions)

# cluster_data = {attributes[i]: [centers[j][i] for j in range(k)]  for i in range(len(attributes))}
# cluster_data = pd.DataFrame.from_dict(cluster_data)
# print(cluster_data)

# plot_attrs = ["goals", "npxg", "tackles", "passes_completed_short", "progressive_carries", "through_balls", "interceptions"]
# radar_plot(cluster_data, plot_attrs, k)
# parallel_coordinates(cluster_data, unique_colors, plot_attrs)

# data = {idx: data[labels == idx] for idx in range(k)}
# print(centers)
