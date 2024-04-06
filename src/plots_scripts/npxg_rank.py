import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import argparse
import numpy as np
import matplotlib.pyplot as plt

data_path = f"./../../datasets/2023-2024/Serie-A/players.csv"

data = pd.read_csv(data_path)

if data["minutes"].dtype != "int64":
    data["minutes"] = data["minutes"].apply(lambda x: int(x.replace(",", ""))).astype("int64")

data = data[data["minutes"] >= 500]

stat = "npxg_per_shot"
stat = "npxg_per90"
stat = "goals_pens_per90"
stat = "npxg_net"
data[stat] = data[stat]/data["minutes"]*90

data = data[["player_id", "player", stat]].sort_values(stat, ascending=False)
for i in range(len(data)):
    print(f"{i+1}: {data.iloc[i, 1]}: {data.iloc[i, 2]}")