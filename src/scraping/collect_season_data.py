import pandas as pd
import os
import argparse
from utils import *

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")

args = parser.parse_args()


if args.all_comps:
    leagues_dir = f"./../../datasets/{args.season}/All-Competitions/"
else:
    leagues_dir = f"./../../datasets/{args.season}/"

if not os.path.exists(leagues_dir):
    print(f"{leagues_dir} doesn't exist")
    exit()

print(leagues_dir)
teams_dirs = [d for d in os.listdir(leagues_dir) if os.path.isdir(os.path.join(leagues_dir, d))]
if not args.all_comps:
    teams_dirs.remove("All-Competitions")
teams_dirs.remove("Champions-League")

players_df_list = []
team_df_list = []
gk_df_list = []
opponents_df_list = []

for dir in teams_dirs:
    team_dir = leagues_dir + dir + "/"
    
    players_df = pd.read_csv(team_dir + "players.csv")
    gk_df = pd.read_csv(team_dir + "goalkeepers.csv")
    players_df_list.append(players_df)
    gk_df_list.append(gk_df)

    if not args.all_comps:
        team_df = pd.read_csv(team_dir + "team.csv")
        opponents_df = pd.read_csv(team_dir + "opponents.csv")
        opponents_df_list.append(opponents_df)
        team_df_list.append(team_df)



players_conc_df = pd.concat(players_df_list)
gk_conc_df = pd.concat(gk_df_list)
players_conc_df.to_csv(f"{leagues_dir}/players.csv", index=False)
gk_conc_df.to_csv(f"{leagues_dir}/goalkeepers.csv", index=False)

if not args.all_comps:
    team_conc_df = pd.concat(team_df_list)
    opponents_conc_df = pd.concat(opponents_df_list)
    team_conc_df.to_csv(f"{leagues_dir}/team.csv", index=False)
    opponents_conc_df.to_csv(f"{leagues_dir}/opponents.csv", index=False)