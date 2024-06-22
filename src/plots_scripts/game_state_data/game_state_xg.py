import argparse
import os
import pandas as pd
# from utils.download_league_match_logs import get_league_match_logs

def parse_minute(minute):

    if type(minute) is int:
        return minute

    if "+" not in minute:
        return int(minute)
    
    minute, extra = minute.split("+")
    return int(minute) + int(extra)


def get_iterator(start, end, exclude_first=False):

    start = str(start); end = str(end)
    # print(start, end)

    if "+" in start:
        start_minute, start_extra = start.split("+")
        start_minute = int(start_minute)
        start_extra = int(start_extra)

        end_minute, end_extra = end.split("+")
        end_minute = int(end_minute)
        end_extra = int(end_extra)

        iterator = [f"{start_minute}+{extra}" for extra in range(start_extra, start_extra+1)]

    elif "+" in end:
        start_minute = int(start)

        end_minute, end_extra = end.split("+")
        end_minute = int(end_minute)
        end_extra = int(end_extra)
        
        iterator = [str(minute) for minute in range(start_minute, end_minute+1)]
        iterator += [f"{end_minute}+{extra}" for extra in range(1, end_extra+1)]
    else:
        start_minute = int(start)
        end_minute = int(end)
        iterator = [str(minute) for minute in range(start_minute, end_minute+1)]

    # print(iterator)

    return iterator


def get_per_minute_state(game_states):

    dict_df = {"minute": [], "state": [], "half": []}
    for idx, half, start, end, state in game_states.itertuples():
        # start = start if idx == 0 else start + 1
        for i in get_iterator(start, end):
            dict_df["minute"].append(i)
            dict_df["state"].append(state)
            dict_df["half"].append(half)
    df = pd.DataFrame.from_dict(dict_df)
    df = df[~df['minute'].duplicated(keep='first')]
    return df

def get_extra_time(game_states):
    first_extra  = game_states[game_states["half"] == "first"].iloc[-1]["end_minute"]
    second_extra  = game_states[game_states["half"] == "second"].iloc[-1]["end_minute"]
    return first_extra, second_extra


def merge_tables(game_states, shots):
    first_extra, second_extra = get_extra_time(game_states)
    game_states = get_per_minute_state(game_states)
    shots['minute'] = shots['minute'].astype(str)
    game_states['minute'] = game_states['minute'].astype(str)
    merged = pd.merge(shots, game_states, on='minute', how='inner')
    return merged, first_extra, second_extra


def compute_states_time(game_states):
    win_time, draw_time, lose_time = 0, 0, 0
    current_half = ""
    for idx, half, start_minute, end_minute, state in game_states.itertuples():
        start_minute = parse_minute(start_minute)
        end_minute = parse_minute(end_minute)
        time_elapsed = end_minute - start_minute

        if current_half != half:
            time_elapsed += 1
            current_half = half

        if state == "win":
            win_time += time_elapsed
        elif state == "draw":
            draw_time += time_elapsed
        if state == "lose":
            lose_time += time_elapsed

    # print(win_time)
    # print(draw_time)
    # print(lose_time)

    return win_time, draw_time, lose_time


parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")
parser.add_argument('--data_path', default="./../../../datasets/", type=str)
args = parser.parse_args()


data_path = args.data_path
season = args.season
league = args.league
all_comps = args.all_comps

base_path = f"{data_path if data_path[-1] == '/' else data_path + '/'}{season}{f'/All-Competitions' if all_comps else ''}{f'/{league}' if league != '' else ''}/"


teams_dirs = [base_path + d + "/" for d in os.listdir(base_path) if not d.endswith(".csv")]

teams_data = {}

for team_dir in teams_dirs:
    team_name = team_dir.split("/")[-2]
    teams_data[team_name] = {
        "win_time": 0,
        "draw_time": 0,
        "lose_time": 0,
        "xg_win": 0,
        "xg_draw": 0,
        "xg_lose": 0,
        "xgot_win": 0,
        "xgot_draw": 0,
        "xgot_lose": 0,
        "npxgot_win": 0,
        "npxgot_draw": 0,
        "npxgot_lose": 0,
        "goals_win": 0,
        "goals_draw": 0,
        "goals_lose": 0,
        "npgoals_win": 0,
        "npgoals_draw": 0,
        "npgoals_lose": 0,
        "npxg_win": 0,
        "npxg_draw": 0,
        "npxg_lose": 0,
        "shots_win": 0,
        "shots_draw": 0,
        "shots_lose": 0,
        "xg_against_win": 0,
        "xg_against_draw": 0,
        "xg_against_lose": 0,
        "npxg_against_win": 0,
        "npxg_against_draw": 0,
        "npxg_against_lose": 0,
        "shots_against_win": 0,
        "shots_against_draw": 0,
        "shots_against_lose": 0,
        "xgot_against_win": 0,
        "xgot_against_draw": 0,
        "xgot_against_lose": 0,
        "npxgot_against_win": 0,
        "npxgot_against_draw": 0,
        "npxgot_against_lose": 0,
        "goals_against_win": 0,
        "goals_against_draw": 0,
        "goals_against_lose": 0,
        "npgoals_against_win": 0,
        "npgoals_against_draw": 0,
        "npgoals_against_lose": 0,
    }

    if team_dir != "./../../../datasets/2023-2024/Serie-A/Inter/":
        continue

    match_logs = team_dir + "matchlogs/"

    matches = os.listdir(match_logs)
    matches = sorted(matches, key=lambda x: int(x.split("_")[-1]))
    matches = [match_logs + d + "/" for d in matches]
    
    for match in matches:      

        game_states = pd.read_csv(match + "game_states.csv")
        shots = pd.read_csv(match + "shots.csv")
        shots, first_extra, second_extra = merge_tables(game_states, shots)
        win_time, draw_time, lose_time = compute_states_time(game_states)

        teams_data[team_name]["win_time"] += win_time
        teams_data[team_name]["draw_time"] += draw_time
        teams_data[team_name]["lose_time"] += lose_time
        
        for idx, row in shots.iterrows():
            scored = row["scored"]
            team = row["team"]
            xg = row["xg"]
            xgot = row["xgot"]
            penalty = row["penalty"]
            state = row["state"]
        
            venue = "against_" if team == "away" else ""

            teams_data[team_name][f"xg_{venue}{state}"] += xg
            teams_data[team_name][f"xgot_{venue}{state}"] += xgot

            if scored:
                teams_data[team_name][f"goals_{venue}{state}"] += 1

            if not penalty:
                teams_data[team_name][f"npxg_{venue}{state}"] += xg
                teams_data[team_name][f"npxgot_{venue}{state}"] += xgot
                teams_data[team_name][f"shots_{venue}{state}"] += 1

                if scored:
                    teams_data[team_name][f"npgoals_{venue}{state}"] += 1

    for key in teams_data[team_name].keys():
        print(key, teams_data[team_name][key])

                
