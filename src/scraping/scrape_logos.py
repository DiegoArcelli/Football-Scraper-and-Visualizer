import requests
from bs4 import BeautifulSoup
import argparse
from utils import *
import time
import shutil

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
args = parser.parse_args()

def get_team_stats(team, team_url):

    response = requests.get(team_url)

    if response.status_code == 200:
        html_content = response.text
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        exit()

    soup = BeautifulSoup(html_content, 'html.parser')
    team_logo_url = soup.select('img[class="teamlogo"]')[0].get("src")
    r = requests.get(team_logo_url, stream=True)
    if r.status_code == 200:
        with open(f"./../../images/{team}.png", 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)        


def get_league_dataset(league_name, season):

    league_id = league_to_id_map[league_name]


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
        team_url_components = team_url.split("/")
        ref_pos = team_url_components.index("squads", 0, len(team_url_components)) + 2
        url_league_id = f"c{league_id}"
        team_url_components = team_url_components[:ref_pos] + [season, url_league_id] + team_url_components[ref_pos:]
        team_url = base_url + "/".join(team_url_components) + f"-{league_name}"
        print(team_name, team_url)
        # time.sleep(5)
        get_team_stats(team_name, team_url)


league_name = args.league
season = args.season

get_league_dataset(league_name, season)