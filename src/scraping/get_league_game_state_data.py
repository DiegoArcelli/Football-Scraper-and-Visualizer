import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import argparse
from pyppeteer.errors import TimeoutError, BrowserError
from utils import *
import time
import copy
import os

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
args = parser.parse_args()

league_name = args.league
season = args.season

def get_minute(minute):

    if type(minute) is int:
        return minute

    if "+" not in minute:
        return int(minute)
    
    minute, extra = minute.split("+")
    return int(minute)


def extract_game_state_info(match_log_path):

    shots_data = pd.read_csv(match_log_path)

    init_stats_dict = {
        "xg": 0.0,
        "np_xg": 0.0,
        "xgot": 0.0,
        "np_xgot": 0.0,
        "shots": 0,
        "penalties": 0,
        "goals": 0,
        "np_goals": 0,
    }

    teams_data = {team: {state : copy.deepcopy(init_stats_dict) for state in ["draw", "win", "lose"]} for team in ["home", "away"]}
    game_data = {"home": 0, "away": 0}
    minutes_data = {team: {state : 0 for state in ["draw", "win", "lose"]} for team in ["home", "away"]}

    home_state = "draw"
    away_state = "draw"
    global_state = "draw"

    ref_minute = 0

    for shot in shots_data.itertuples():
        minute = shot.minute
        team = shot.team
        scored = shot.scored
        xg = shot.xg
        xgot = shot.xgot
        penalty = shot.penalty

        state = home_state if team == "home" else away_state
        
        teams_data[team][state]["xg"] += xg
        teams_data[team][state]["xgot"] += xgot

        if scored:
            teams_data[team][state]["goals"] += 1
            game_data[team] += 1

        if not penalty:
            teams_data[team][state]["np_xg"] += xg
            teams_data[team][state]["np_xgot"] += xgot
            teams_data[team][state]["shots"] += 1
            if scored:
                teams_data[team][state]["np_goals"] += 1
        else:
            teams_data[team][state]["penalties"] += 1
            if scored:
                teams_data[team][state]["goals"] += 1

        # update_game state

        if game_data["home"] > game_data["away"]:
            new_global_state = "home_win"
        elif game_data["home"] < game_data["away"]:
            new_global_state = "away_win"
        else:
            new_global_state = "draw"

        if new_global_state != global_state:
            minute = get_minute(minute)
            time_spent_in_state = minute-ref_minute

            minutes_data["home"][home_state] += time_spent_in_state
            minutes_data["away"][away_state] += time_spent_in_state

            if new_global_state == "home_win":
                home_state = "win"
                away_state = "lose"
            elif new_global_state == "away_win":
                home_state = "lose"
                away_state = "win"
            else:
                home_state = "draw"
                away_state = "draw"

            global_state = new_global_state
            ref_minute = minute

    time_spent_in_state = 90-ref_minute
    minutes_data["home"][home_state] += time_spent_in_state
    minutes_data["away"][away_state] += time_spent_in_state
    # print(minutes_data)

    for team in ["home", "away"]:
        for state in ["win", "draw", "lose"]:
            teams_data[team][state]["minutes"] = minutes_data[team][state]
            # teams_data[team][state]["xg"] = round(teams_data[team][state]["xg"])
            # teams_data[team][state]["np_xg"] = round(teams_data[team][state]["np_xg"])
            # teams_data[team][state]["xgot"] = round(teams_data[team][state]["xgot"])
            # teams_data[team][state]["np_xgot"] = round(teams_data[team][state]["np_xgot"])

    return teams_data


season_dir = f"./../../datasets/{season}/{league_name}"

teams_df = pd.read_csv(f"{season_dir}/team.csv")
teams = teams_df["team"].apply(lambda x: x.replace(" " ,"-"))

teams = ["Inter", "Milan", "Juventus"]

league_file_content = "team,match_id,xg,xgot,goals,np_xg,np_xgot,np_goals,penalties,shots,minutes\n"
league_opponent_file_content = "team,match_id,xg,xgot,goals,np_xg,np_xgot,np_goals,penalties,shots,minutes\n"

for team in teams:
    team_matchlogs_dir = f"{season_dir}/{team}/matchlogs/"
    team_dir =f"{season_dir}/{team}/"
    matches =  [file for file in os.listdir(team_matchlogs_dir) if file.endswith(".csv")]

    matches.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
    matches_path = [f"{team_matchlogs_dir}{file}" for file in matches]

    team_file_content = "team,match_id,state,xg,xgot,goals,np_xg,np_xgot,np_goals,penalties,shots,minutes\n"
    opponent_file_content = "team,match_id,state,xg,xgot,goals,np_xg,np_xgot,np_goals,penalties,shots,minutes\n"
    match_id = 0

    for match_path in matches_path:
        print(match_path)
        game_state = extract_game_state_info(match_path)

        for state in ["win", "draw", "lose"]:
            team_file_content += f"{team},{match_id},{state},{game_state['home'][state]['xg']},{game_state['home'][state]['xgot']},{game_state['home'][state]['goals']},{game_state['home'][state]['np_xg']},{game_state['home'][state]['np_xgot']},{game_state['home'][state]['np_goals']},{game_state['home'][state]['penalties']},{game_state['home'][state]['shots']},{game_state['home'][state]['minutes']}\n"
            league_file_content += f"{team},{match_id},{game_state['home'][state]['xg']},{game_state['home'][state]['xgot']},{game_state['home'][state]['goals']},{game_state['home'][state]['np_xg']},{game_state['home'][state]['np_xgot']},{game_state['home'][state]['np_goals']},{game_state['home'][state]['penalties']},{game_state['home'][state]['shots']},{game_state['home'][state]['minutes']}\n"

        for state in ["win", "draw", "lose"]:
            opponent_file_content += f"{team},{match_id},{state},{game_state['away'][state]['xg']},{game_state['away'][state]['xgot']},{game_state['away'][state]['goals']},{game_state['away'][state]['np_xg']},{game_state['away'][state]['np_xgot']},{game_state['away'][state]['np_goals']},{game_state['away'][state]['penalties']},{game_state['away'][state]['shots']},{game_state['away'][state]['minutes']}\n"
            league_opponent_file_content += f"{team},{match_id},{state},{game_state['away'][state]['xg']},{game_state['away'][state]['xgot']},{game_state['away'][state]['goals']},{game_state['away'][state]['np_xg']},{game_state['away'][state]['np_xgot']},{game_state['away'][state]['np_goals']},{game_state['away'][state]['penalties']},{game_state['away'][state]['shots']},{game_state['away'][state]['minutes']}\n"

        match_id += 1

    team_file = f"{season_dir}/{team}/team_game_state.csv"
    with open(team_file, "w") as f:
        f.write(team_file_content)

    team_file = f"{season_dir}/{team}/opponents_game_state.csv"
    with open(team_file, "w") as f:
        f.write(opponent_file_content)



team_file = f"{season_dir}/team_game_state.csv"
with open(team_file, "w") as f:
    f.write(league_file_content)

team_file = f"{season_dir}/opponents_game_state.csv"
with open(team_file, "w") as f:
    f.write(league_opponent_file_content)

    