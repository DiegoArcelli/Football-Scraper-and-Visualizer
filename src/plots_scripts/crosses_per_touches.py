import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import argparse

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="", type=str)
parser.add_argument('--season', default="2023-2024", type=str)

args = parser.parse_args()

season = args.season
league = args.league


teamsto_show = [
    "Milan",
    "Juventus",
    "Inter",
    "Lazio",
    "Roma",
    "Atalanta",
    "Napoli",
    "Fiorentina"
]

if league != "":
    data_path = f"./../../datasets/{season}/{league}/team.csv"
else:
    data_path = f"./../../datasets/{season}/team.csv"

data = pd.read_csv(data_path)


touches = data["touches"]
crosses = data["crosses"]

ref_touches = 500

stat_name = f"crosses_per_{ref_touches}_touches"
crosses_per_touches = (crosses/touches)*ref_touches
data[stat_name] = crosses_per_touches

team_rank = data[["team", stat_name]].sort_values(by=[stat_name], ascending=False)
for i in range(len(team_rank)):
    print(f"{i+1}) {team_rank.iloc[i, 0]}: {team_rank.iloc[i, 1]}")


avg = team_rank[stat_name].mean()
med = team_rank[stat_name].median()
std = team_rank[stat_name].std()

print(f"Average: {avg}")
print(f"Median: {med}")
print(f"Standard deviation: {std}")