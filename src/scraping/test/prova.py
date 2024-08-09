import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
from pyppeteer.errors import TimeoutError, BrowserError
# from utils import *
import copy
import time
import os
import re
from functools import cmp_to_key


def parse_minute(minute):

    if type(minute) is int:
        return minute

    if "+" not in minute:
        return int(minute)
    
    minute, extra = minute.split("+")
    return int(minute) + int(extra)



def compute_half_game_state(
        goals_minute,
        ref_minute="1",
        home_goals=0,
        away_goals=0,
        start_state="draw"
    ):

    def check_interval(minute, lower, upper):
        minute = int(minute.split("+")[0])
        lower = int(lower)
        upper = int(upper)

        if minute >= lower and minute <= upper:
            return True

        return False

    assert ref_minute in ["1", "46", "91", "106"], "Error"

    
    if ref_minute == "1":
        period = "first_half"; last_minute=45
    elif ref_minute == "46":
        period = "second_half"; last_minute=90
    elif ref_minute == "91":
        period = "first_half_overtime"; last_minute=105
    elif ref_minute == "106":
        period = "first_half_overtime"; last_minute=120

    # goals_minute = [venue, minute for venue, minute in goals_minute if minute.split("+")[0] >= int(ref_minute) and minute.split("+")[0] <= last_minute]
    goals_minute = [(venue, minute) for (venue, minute) in goals_minute if check_interval(minute, ref_minute, last_minute)]

    # if goals_minute == []:
    #     return None

    # ref_minute = 1
    # state = "draw"
    states = []
    state = start_state

    for team, minute in goals_minute:

        if team == "home":
            home_goals += 1
        else:
            away_goals += 1

        if home_goals > away_goals:
            new_state = "win"
        elif home_goals < away_goals:
            new_state = "lose"
        else:
            new_state = "draw"

        if new_state != state:
            #minutes_in_state = minute - ref_minute
            states.append((period, ref_minute, minute, state))
            state = new_state
            ref_minute = minute
    
    states.append(("second", ref_minute, f"{period}_end", state))
        
    return states, home_goals, away_goals, state



def parse_event_panel(soup, venue):

    class Minute:

        def __init__(self, minute):
            self.minute = minute

        def __repr__(self):
            return self.minute

        def __gt__(self, other):

            x = self.minute; y = other.minute

            if "+" in x:
                x_min, x_extra = x.split("+")
                x_min = int(x_min); x_extra = int(x_extra)
            else:
                x_min = int(x); x_extra = None

            if "+" in y:
                y_min, y_extra = y.split("+")
                y_min = int(y_min); y_extra = int(y_extra)
            else:
                y_min = int(y); y_extra = None

            # both have extra time
            if x_extra is not None and y_extra is not None and x_min == y_min:
                return x_extra > y_extra

            return x_min > y_min


    scorebox = soup.select("div[class='scorebox']")[0]

    if venue == "Home":
        team_events = scorebox.select('div#a.event')[0]
        opponent_events = scorebox.select('div#b.event')[0]
    else:
        team_events = scorebox.select('div#b.event')[0]
        opponent_events = scorebox.select('div#a.event')[0]

    team_events = [event for event in team_events.children if event.name == 'div']
    opponent_events = [event for event in opponent_events.children if event.name == 'div'] 

    goals_minute = []

    for team, events in [("home", team_events), ("away", opponent_events)]:
        for event in events:

            event_type = event.select("div[class^='event']")[0].get("class")
            
            if type(event_type) == list:
                event_type = event_type[-1]

            if event_type.endswith("goal"):
                minute = event.text.split('·')[-1]
                minute = minute.replace(" ", "")
                minute = minute.replace("’", "")
                goals_minute.append((team, Minute(minute)))

    # goals_minute.sort(key=lambda x: x[1])
    goals_minute = sorted(goals_minute, key=lambda x: x[1])
    goals_minute = [(venue, m.minute) for venue, m in goals_minute]    

    home_goals = 0; away_goals = 0; state = "draw"
    states = []

    for ref_minute in ["1", "46", "91", "106"]:
        output = compute_half_game_state(
            goals_minute=goals_minute,
            ref_minute=ref_minute,
            home_goals=home_goals,
            away_goals=away_goals,
            start_state=state
        )

        if output is None:
            break

        half_states, home_goals, away_goals, state = output
        states = states + half_states

    return states



def parse_shooting_table(soup, team_id, venue):

    #parse_event_panel(soup, venue)

    shots_table = soup.select('table[id="shots_all"]')[0]
    shots_info = shots_table.select('tr[class^="shots_"]')

    match_shots_info = []
    for shot_info in shots_info:
        player = shot_info.select('td[data-stat="player"]')[0]
        player_name = player.text
        shot_player_id = player.a.get("href").split("/")[3]
        penalty = True if "(pen)" in player.text else False
        minute = shot_info.select('th[data-stat="minute"]')[0].text
        outcome = shot_info.select('td[data-stat="outcome"]')[0].text
        outcome = True if outcome == "Goal" else False
        xg = shot_info.select('td[data-stat="xg_shot"]')[0].text
        xgot = shot_info.select('td[data-stat="psxg_shot"]')[0].text
        xgot = "0" if xgot == "" else xgot
        
        shot_team_id = shot_info.select('td[data-stat="team"]')[0].select("a")[0].get("href").split("/")[3]
        team = "home" if shot_team_id == team_id else "away"

        match_shots_info.append((minute, team, player_name, shot_player_id, outcome, xg, xgot, penalty))

    # minutes = list(map(lambda x: x[0], match_shots_info))
    # first_half_minute = [minute for minute in minutes if minute[:2] == "45"]
    # second_half_minute = [minute for minute in minutes if minute[:2] == "90"]
    # first_half_minutes = "45" if first_half_minute == [] else first_half_minute[-1]
    # second_half_minutes = "90" if second_half_minute == [] else second_half_minute[-1]

    game_states = parse_event_panel(soup, venue)

    return match_shots_info, game_states
    

url = "https://fbref.com/en/matches/e70ac4b1/Internazionale-Sassuolo-September-27-2023-Serie-A"
# url = "https://fbref.com/en/partite/254420f7/Internazionale-Monza-19-Agosto-2023-Serie-A"
# url = "https://fbref.com/en/matches/eb1af48a/Juventus-Lecce-September-26-2023-Serie-A"
# url = "https://fbref.com/en/matches/14cf8fd1/Sassuolo-Juventus-September-23-2023-Serie-A"
# url = "https://fbref.com/en/matches/8b6e8a62/Udinese-Juventus-August-20-2023-Serie-A"
# url = "https://fbref.com/en/matches/ce6440ec/Genoa-Internazionale-December-29-2023-Serie-A"
# url = "https://fbref.com/en/matches/b0d9b0e1/Manchester-City-Real-Madrid-April-17-2024-Champions-League"
# url = "https://fbref.com/en/partite/7140acae/Argentina-France-18-Dicembre-2022-World-Cup"

response = requests.get(url)
print(url)

if response.status_code == 200:
    html_content = response.text
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
    exit()

soup = BeautifulSoup(html_content, 'html.parser')
match_shots_info, game_states = parse_shooting_table(soup, "jfdklajfsdòkjfsdakòljfasd", "Home")
print(game_states)