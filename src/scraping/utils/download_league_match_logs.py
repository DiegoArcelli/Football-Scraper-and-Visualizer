import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
from pyppeteer.errors import TimeoutError, BrowserError
from .utils import *
import time
import os

def parse_minute(minute):

    if type(minute) is int:
        return minute

    if "+" not in minute:
        return int(minute)
    
    minute, extra = minute.split("+")
    return int(minute) + int(extra)    

def save_matchlogs_table(file_path, shots_list):
    file_content = "minute,team,player,player_id,scored,xg,xgot,penalty\n"
    for (minute, team, player, player_id, outcome, xg, xgot, penalty) in shots_list:
        file_content += f"{minute},{team},{player},{player_id},{outcome},{xg},{xgot},{penalty}\n"
    
    with open(file_path, "w") as match_file:
        match_file.write(file_content)


def save_game_states(file_path, game_states):
    file_content = "start_minute,end_minute,state\n"
    for (minute_start, minute_end, state) in game_states:
        file_content += f"{minute_start},{minute_end},{state}\n"
    
    with open(file_path, "w") as match_file:
        match_file.write(file_content)



def parse_event_panel(soup, venue, first_half_extra, second_half_extra):

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

                if "+" in minute:
                    minute, extra = minute.split("+")
                    minute = int(minute)
                    extra = int(extra)
                    minute = minute + extra + (first_half_extra if minute > 45 else 0)
                else:
                    minute = int(minute)
                
                goals_minute.append((team, minute))
    
    goals_minute.sort(key=lambda x: x[1])
    full_minutes = second_half_extra + 90
    # exit()

    home_goals, away_goals = 0, 0
    ref_minute = 0
    state = "draw"
    states = []
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
            states.append((ref_minute, minute, state))
            state = new_state
            ref_minute = minute

    #minutes_in_state = full_minutes - ref_minute
    states.append((ref_minute, full_minutes, state))
    
    return states



def parse_shooting_table(url, team_id, venue):
    session = HTMLSession()

    is_page_dowloaded = False
    while not is_page_dowloaded:
        try:
            r = session.get(url)
            r.html.render()  # this call executes the js in the page
            is_page_dowloaded = True
        except (TimeoutError, BrowserError):
           print("Retrying download")
           is_page_dowloaded = False 
            
    html_content = r.html.html

    soup = BeautifulSoup(html_content, 'html.parser')

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

    minutes = list(map(lambda x: x[0], match_shots_info))
    first_half_minute = [minute for minute in minutes if minute[:2] == "45"]
    second_half_minute = [minute for minute in minutes if minute[:2] == "90"]
    first_half_minute = 45 if first_half_minute == [] else first_half_minute[-1]
    second_half_minute = 45 if second_half_minute == [] else second_half_minute[-1]
    first_half_minute = parse_minute(first_half_minute)
    second_half_minute = parse_minute(second_half_minute)

    if first_half_minute < 45:
        first_half_extra = 0
    else:
        first_half_extra = first_half_minute - 45

    if second_half_minute < 90:
        second_half_extra = 0
    else:
        second_half_extra = second_half_minute - 90

    game_states = parse_event_panel(soup, venue, first_half_extra, second_half_extra)

    return match_shots_info, game_states
    



def parse_match_table(team, team_url, team_id, league_dir):

    dir_name = team.replace(" ", "-")
    team_dir = f"{league_dir}{dir_name}/matchlogs/"
    create_dir(team_dir)

    session = HTMLSession()
    
    is_page_dowloaded = False
    print(team_url)
    while not is_page_dowloaded:
        try:
            r = session.get(team_url)
            r.html.render()  # this call executes the js in the page
            is_page_dowloaded = True
        except (TimeoutError, BrowserError):
           print("Retrying download")
           is_page_dowloaded = False 
            
    html_content = r.html.html
    # print(html_content)
    soup = BeautifulSoup(html_content, 'html.parser')

    match_table = soup.select('table[id^="matchlogs"]')[0]
    matches = match_table.select('tr')

    match_id = 0
    base_url = "https://fbref.com"

    for match in matches:

        match_file_path = f"{team_dir}match_{match_id}.csv"
        state_file_path = f"{team_dir}states_{match_id}.csv"
        
        if os.path.exists(match_file_path) and os.path.exists(state_file_path):
            match_id += 1
            continue

        match_cell = match.select('td[data-stat="match_report"]')
        if match_cell == []:
            continue


        match_report = match_cell[0].select("a")[0].text
        # match_report = match.select('td[data-stat="match_report"]')[0].select("a")[0].text
        # # print(match_report)
        if match_report != "Match Report":
            return


        match_url = match_cell[0].select('a')

        if match_url == []:
            continue

        venue = match.select('td[data-stat="venue"]')[0].text

        match_url= match_url[0].get("href")
        match_url = f"{base_url}{match_url}"
        print(match_url)

        match_shots, game_states = parse_shooting_table(match_url, team_id, venue)

        save_matchlogs_table(match_file_path, match_shots)
        save_game_states(state_file_path, game_states)

        match_id += 1

        

    # players_df = merge_data_frames(players_tables, "player_id")
    # gk_df = merge_data_frames(gk_tables, "player_id")
    # players_df.to_csv(f"{team_dir}/players.csv", index=False)
    # gk_df.to_csv(f"{team_dir}/goalkeepers.csv", index=False)

    # if not all_comps:
    #     team_df = merge_data_frames(team_tables, "team")
    #     opponent_df = merge_data_frames(opponent_table, "team")
    #     team_df.to_csv(f"{team_dir}/team.csv", index=False)
    #     opponent_df.to_csv(f"{team_dir}/opponents.csv", index=False)


def get_league_match_logs(
        root_dir : str = "./../../datasets/",
        league_name : str = "Serie-A",
        season : str = "2023-2024", 
        all_comps : bool = True
    ) -> None:

    root_dir = root_dir + ("/" if root_dir[-1] != "/" else "")

    season_dir = f"{root_dir}{season}/"
    create_dir(season_dir)

    if all_comps:
        season_dir = f"{root_dir}{season}/All-Competitions/"
        create_dir(season_dir)

    league_dir = f"{season_dir}{league_name}/"
    create_dir(league_dir)

    league_id = get_league_id(league_name)


    base_url = "https://fbref.com"
    url = f"https://fbref.com/en/comps/{league_id}/{season}/{league_name}-Stats"

    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        exit()

    soup = BeautifulSoup(html_content, 'html.parser')
    div = soup.select('div[id^="all_results"]')[-1]
    table = div.select('table[class^="stats_table"]')[0].select('tbody')[0]
    teams = table.select('tr')

    for team in teams:
        team_stats = team.select('td[data-stat="team"]')[0]

        if  len(team_stats.select("a")) == 0:
            continue

        team_info = team_stats.select("a")[0]
        team_name = team_info.text
        team_url = team_info.get("href")
        team_url_components = team_url.split("/")[1:]
        team_id = team_url_components[2]
        team_name_url = "-".join(team_url_components[3].split("-")[:-1])

        team_url = f"{base_url}/en/squads/{team_id}/{season}/matchlogs/c{league_id}/schedule/{team_name_url}-Scores-and-Fixtures-{league_name}"
        # ref_pos = team_url_components.index("squads", 0, len(team_url_components)) + 2
        # url_league_id = "all_comps" if all_comps else f"c{league_id}"
        # team_url_components = team_url_components[:ref_pos] + [season, url_league_id] + team_url_components[ref_pos:]
        # team_url = base_url + "/".join(team_url_components) + f"-{league_name}"
        # print(team_name, team_url)
        time.sleep(3)
        parse_match_table(team_name, team_url, team_id, league_dir)
        print("")