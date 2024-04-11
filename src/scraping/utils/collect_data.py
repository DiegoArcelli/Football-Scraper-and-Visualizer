import pandas as pd
import argparse
import os
from .utils import *

def collect_league_data(
    league_name : str,
    season : str,
    all_comps : bool,
    root_dir : str
):
    # if args.all_comps:
    #     league_dir = f"./../../datasets/{args.season}/All-Competitions/{args.league}/"
    # else:
    #     league_dir = f"./../../datasets/{args.season}/{args.league}/"
    if all_comps:
        league_dir = f"{root_dir}{season}/All-Competitions/{league_name}/"
    else:
        league_dir = f"{root_dir}{season}/{league_name}/"

    if not os.path.exists(league_dir):
        print(f"{league_dir} doesn't exist")
        exit()

    teams_dirs = [d for d in os.listdir(league_dir) if os.path.isdir(os.path.join(league_dir, d))]

    players_df_list = []
    team_df_list = []
    gk_df_list = []
    opponents_df_list = []


    for dir in teams_dirs:
        team_dir = league_dir + dir + "/"

        players_df = pd.read_csv(team_dir + "players.csv")
        gk_df = pd.read_csv(team_dir + "goalkeepers.csv")
        players_df_list.append(players_df)
        gk_df_list.append(gk_df)

        if not all_comps:
            team_df = pd.read_csv(team_dir + "team.csv")
            opponents_df = pd.read_csv(team_dir + "opponents.csv")
            team_df_list.append(team_df)
            opponents_df_list.append(opponents_df)


    print(f"\nCollecting {league_name} {season} data in {league_dir}")

    players_conc_df = pd.concat(players_df_list)
    gk_conc_df = pd.concat(gk_df_list)
    players_conc_df.to_csv(f"{league_dir}/players.csv", index=False)
    gk_conc_df.to_csv(f"{league_dir}/goalkeepers.csv", index=False)

    if not all_comps:
        team_conc_df = pd.concat(team_df_list)
        opponents_conc_df = pd.concat(opponents_df_list)
        team_conc_df.to_csv(f"{league_dir}/team.csv", index=False)
        opponents_conc_df.to_csv(f"{league_dir}/opponents.csv", index=False)



def collect_season_data(
    league_name : str,
    season : str,
    all_comps : bool,
    root_dir : str
):
    # if args.all_comps:
    #     leagues_dir = f"./../../datasets/{args.season}/All-Competitions/"
    # else:
    #     leagues_dir = f"./../../datasets/{args.season}/"

    if all_comps:
        leagues_dir = f"{root_dir}{season}/All-Competitions/"
    else:
        leagues_dir = f"{root_dir}{season}/"


    if not os.path.exists(leagues_dir):
        print(f"{leagues_dir} doesn't exist")
        exit()

    teams_dirs = [d for d in os.listdir(leagues_dir) if os.path.isdir(os.path.join(leagues_dir, d))]
    if not all_comps:
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

        if not all_comps:
            team_df = pd.read_csv(team_dir + "team.csv")
            opponents_df = pd.read_csv(team_dir + "opponents.csv")
            opponents_df_list.append(opponents_df)
            team_df_list.append(team_df)


    print(f"\nCollecting season {season} data in {leagues_dir}")

    players_conc_df = pd.concat(players_df_list)
    gk_conc_df = pd.concat(gk_df_list)
    players_conc_df.to_csv(f"{leagues_dir}/players.csv", index=False)
    gk_conc_df.to_csv(f"{leagues_dir}/goalkeepers.csv", index=False)

    if not all_comps:
        team_conc_df = pd.concat(team_df_list)
        opponents_conc_df = pd.concat(opponents_df_list)
        team_conc_df.to_csv(f"{leagues_dir}/team.csv", index=False)
        opponents_conc_df.to_csv(f"{leagues_dir}/opponents.csv", index=False)