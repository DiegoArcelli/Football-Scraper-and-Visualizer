# shooting history format

import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import argparse
import urllib
from pyppeteer.errors import TimeoutError, BrowserError
from .utils import get_league_id, create_dir


def adjust_prob(xg, prev_xg):
    xg = float(xg)
    prev_xg = float(xg)
    adj_xg = prev_xg + (1-prev_xg)*xg
    adj_xg = str(round(adj_xg, 2))
    return adj_xg


def get_minutes_played(soup, player_id):

    def parse_table(table, player_id):

        table_body = table.select('tbody')[0]
        players = table_body.find_all('tr')

        for player in players:
            p_id = player.select('th[data-stat="player"]')[0].get("data-append-csv")
            minutes = player.select('td[data-stat="minutes"]')[0].text
            if p_id == player_id:
                return minutes
            
        return 0

    tables = soup.find_all('table', {'id': lambda x: x and x.startswith("stats_") and x.endswith("_summary")})

    minutes = parse_table(tables[0], player_id)
    if minutes != 0:
        return minutes
    
    minutes = parse_table(tables[1], player_id)
    if minutes != 0:
        return minutes
    
    return "0"

def parse_shooting_table(url, player_id, match_id):
    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        exit()

    soup = BeautifulSoup(html_content, 'html.parser')

    minutes_played = get_minutes_played(soup, player_id)

    shots_table = soup.select('table[id="shots_all"]')[0]
    shots_info = shots_table.select('tr[class^="shots_"]')

    match_shots_info = []
    match_minutes_info = []
    for shot_info in shots_info:
        player = shot_info.select('td[data-stat="player"]')[0]
        shot_player_id = player.a.get("href").split("/")[3]
        
        if shot_player_id != player_id:
            continue

        sca = shot_info.select('td[data-stat="sca_1_player"]')[0].select("a")

        # compose = False
        # if sca != []:
        #     player_sca = sca[0].get("href").split("/")[3]

        #     sca_type = shot_info.select('td[data-stat="sca_1_type"]')[0].text
        
        #     if player_sca == player_id and sca_type == "Shot":
        #         compose = True

        penalty = True if "(pen)" in player.text else False
        minute = shot_info.select('th[data-stat="minute"]')[0].text
        outcome = shot_info.select('td[data-stat="outcome"]')[0].text
        outcome = True if outcome == "Goal" else False
        xg = shot_info.select('td[data-stat="xg_shot"]')[0].text
        xgot = shot_info.select('td[data-stat="psxg_shot"]')[0].text
        xgot = "0" if xgot == "" else xgot

        # if compose:
        #     _, prev_xg, prev_xgot, _ = match_shots_info[-1]
        #     xg = adjust_prob(xg, prev_xg)
        #     xgot = adjust_prob(xgot, prev_xgot)
        #     return xg, xgot
            

        match_shots_info.append((match_id, minute, outcome, xg, xgot, penalty))

    return match_shots_info, (match_id, minutes_played)
    



def get_shooting_history(
        root_dir : str = "./../../datasets/",
        player_id : str = "79443529",
        league_name : str = "Serie-A",
        season : str = "2023-2024", 
    ) -> None:

    root_dir = root_dir + ("/" if root_dir[-1] != "/" else "")

    league_id = get_league_id(league_name) if league_name != "All-Comp" else ""

    base_url = "https://fbref.com"
    url = f"{base_url}/en/players/{player_id}/matchlogs/{season}/c{league_id}/"
    print(url)

    response = requests.get(url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        exit()

    soup = BeautifulSoup(html_content, 'html.parser')

    player_name = soup.select('div[id="info"]')[0].select('div[id="meta"]')[0].select("h1")[0].select("span")[0].text

    match_table = soup.select('table[id^="matchlogs"]')[0]
    matches = match_table.select('tr')

    matches_url = []
    matches_shots = []
    matches_minutes = []
    match_id = 0
    for match in matches:

        match_cell = match.select('td[data-stat="match_report"]')

        if match_cell == []:
            continue

        match_url = match_cell[0].select('a')

        if match_url == []:
            continue

        match_url= match_url[0].get("href")
        match_url = f"{base_url}{match_url}"
        print(match_url)
        match_shots, match_minutes = parse_shooting_table(match_url, player_id, match_id)
        matches_shots.append(match_shots)
        matches_minutes.append(match_minutes)

        match_id += 1

    matches_shots = [shot_info for shots_info in matches_shots for shot_info in shots_info]

    file_dir = f"{root_dir}shots/{player_id}"
    create_dir(file_dir)
    file_dir = f"{file_dir}/{season}"
    create_dir(file_dir)

    print(f"Saving {player_name} ({player_id}) shooting history for {league_name} {season} in {file_dir + '/'}")

    file_path = f"{file_dir}/{league_name}.csv"

    file_content = "match_id,minutes,xg,xgot,scored,penalty\n"
    for match_id, minutes, gol, xg, xgot, penalty in matches_shots:
        shot_row = f"{match_id},{minutes},{xg},{xgot},{'True' if gol else 'False'},{'True' if penalty else 'False'}\n"
        file_content += shot_row

    with open(file_path, "w") as file:
        file.write(file_content)


    file_content = "match_id,minutes_played\n"
    for match_id, minute in matches_minutes:
        row = f"{match_id},{minute}\n"
        file_content += row

    file_path = f"{file_dir}/minutes.csv"


    with open(file_path, "w") as file:
        file.write(file_content)


    player_name_file_path = f"{root_dir}shots/{player_id}/name"
    with open(player_name_file_path, "w") as file:
        file.write(player_name)

