import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
import re
from sklearn.decomposition import PCA
import seaborn as sns


from pandas.io.formats.style_render import DataFrame
from tqdm import tqdm
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn import metrics
from math import ceil
import argparse

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--threshold', default=200, type=int)
parser.add_argument('--p90', action="store_true")
args = parser.parse_args()

season = args.season
league = args.league
threshold = args.threshold
all_comps = args.all_comps

data_path = f"./../../datasets/{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/players.csv"

data = pd.read_csv(data_path)

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[data["minutes"] > threshold]

k = 2
kmeans = KMeans(n_clusters=k, n_init=100, max_iter=1000)

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

n_attrs = len(attributes)
data = data[attributes]

corr = data.corr()
corr.style.background_gradient(cmap='coolwarm').set_precision(2)

fig, ax = plt.subplots(figsize=(12,10))

sns.heatmap(corr, 
        xticklabels=corr.columns,
        yticklabels=corr.columns, ax=ax)

# plt.show()

for i in range(n_attrs):
    for j in range(i+1, n_attrs):
        if corr.iloc[i, j] > 0.8:
            print(attributes[i], attributes[j], corr.iloc[i, j])
    print("")
     