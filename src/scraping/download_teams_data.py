import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
import argparse
from pyppeteer.errors import TimeoutError, BrowserError
from utils import *
import time

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--league', default="Serie-A", type=str)
parser.add_argument('--season', default="2023-2024", type=str)
parser.add_argument('--all_comps', action="store_true")
args = parser.parse_args()


def parse_table(table, team_name, all_comps):

    players_stats = {}
    team_stats = {}
    opponent_stats = {}

    table_header = table.select('thead')[0]
    table_body = table.select('tbody')[0]
    if not all_comps:
        table_foot = table.select('tfoot')[0]

    players = table_body.select('tr[data-row]')

    col_names = table_header.select('tr')[1].select('th')
    # attributes_names = []
    attributes_keys = []

    attribute_names_map = {}

    players_stats["player_id"] = []
    players_stats["team"] = []

    for col_name in col_names:
        attribute_name = col_name.get('aria-label')
        attribute_key = col_name.get('data-stat')

        if attribute_key == "matches":
            continue

        # attributes_names.append(attribute_name)
        attributes_keys.append(attribute_key)
        attribute_names_map[attribute_key] = attribute_name
        
        players_stats[attribute_key] = []

        if attribute_name not in ["Player", "Nation", "Position"]:
            team_stats[attribute_key] = []
            opponent_stats[attribute_key] = []


    # get players stats
    for player in players:
        # player_id = player.select('th')[0].get("data-append-csv")
        if len(player.select('a')) > 0:
            player_id = player.select('th')[0].get("data-append-csv")
            player_name = player.select('a')[0].text

            # print(player_id, player_name)
            players_stats["player_id"].append(player_id)
            players_stats["player"].append(player_name)
            players_stats["team"].append(team_name)

            stats = player.select("td")
            for stat in stats:

                stat_text = stat.text

                if stat_text == "Matches":
                    continue

                if stat_text == "":
                    stat_text = None

                attribute = stat.get('data-stat')
                players_stats[attribute].append(stat_text)

    if not all_comps:

        # get team stats
        squad_stats = table_foot.select('tr')[0].select('td')
        team_stats["team"] = [team_name]
        for stat in squad_stats:

            attribute = stat.get('data-stat')
            if attribute in ["nationality", "position", "matches"]:
                continue

            stat_text = stat.text

            if stat_text == "":
                stat_text = None

            
            team_stats[attribute].append(stat_text)

        opp_stats = table_foot.select('tr')[1].select('td')
        opponent_stats["team"] = [team_name]
        for stat in opp_stats:

            attribute = stat.get('data-stat')
            if attribute in ["nationality", "position", "matches"]:
                continue

            stat_text = stat.text

            if stat_text == "":
                stat_text = None

            opponent_stats[attribute].append(stat_text)

    
        return players_stats, team_stats, opponent_stats

    return players_stats


def get_team_stats(team, team_url, league_dir, league_id, all_comps):

    dir_name = team.replace(" ", "-")
    team_dir = f"{league_dir}{dir_name}/"
    create_dir(team_dir)

    session = HTMLSession()

    is_page_dowloaded = False
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

    if all_comps:
        table = soup.select("table#stats_standard_combined")
        if len(table) > 0:
            league_id = "combined"
        else:
            all_comps = False

    tables_names = [
        f"stats_standard_{league_id}",
        f"stats_shooting_{league_id}",
        f"stats_passing_{league_id}",
        f"stats_passing_types_{league_id}",
        f"stats_gca_{league_id}",
        f"stats_defense_{league_id}",
        f"stats_possession_{league_id}",
        f"stats_playing_time_{league_id}",
        f"stats_misc_{league_id}"
    ]

    gk_tables_names = [
        f"stats_keeper_{league_id}",
        f"stats_keeper_adv_{league_id}"
    ]
    
    players_tables = []
    gk_tables = []
    team_tables = []
    opponent_table = []

    for table_name in tables_names:
        # print(f"table#{table_name}")
        table = soup.select(f"table#{table_name}")[0]

        if not all_comps:
            players_stats, team_stats, opponent_stats = parse_table(table, team, all_comps)
            players_df = pd.DataFrame.from_dict(players_stats)
            team_df = pd.DataFrame.from_dict(team_stats)
            opponent_df = pd.DataFrame.from_dict(opponent_stats)
            players_tables.append(players_df)
            team_tables.append(team_df)
            opponent_table.append(opponent_df)
        else:
            players_stats = parse_table(table, team, all_comps)
            players_df = pd.DataFrame.from_dict(players_stats)
            players_tables.append(players_df)


    for gk_table_name in gk_tables_names:
        table = soup.select(f"table#{gk_table_name}")[0]

        if not all_comps:
            gk_stats, team_stats, opponent_stats = parse_table(table, team, all_comps)
            gk_df = pd.DataFrame.from_dict(gk_stats)
            team_df = pd.DataFrame.from_dict(team_stats)
            opponent_df = pd.DataFrame.from_dict(opponent_stats)

            gk_tables.append(gk_df)
            team_tables.append(team_df)
            opponent_table.append(opponent_df)
        else:
            gk_stats = parse_table(table, team, all_comps)
            gk_df = pd.DataFrame.from_dict(gk_stats)
            gk_tables.append(gk_df)

    players_df = merge_data_frames(players_tables, "player_id")
    gk_df = merge_data_frames(gk_tables, "player_id")
    players_df.to_csv(f"{team_dir}/players.csv", index=False)
    gk_df.to_csv(f"{team_dir}/goalkeepers.csv", index=False)

    if not all_comps:
        team_df = merge_data_frames(team_tables, "team")
        opponent_df = merge_data_frames(opponent_table, "team")
        team_df.to_csv(f"{team_dir}/team.csv", index=False)
        opponent_df.to_csv(f"{team_dir}/opponents.csv", index=False)


def get_league_dataset(league_name, season, all_comps):

    season_dir = f"./../../datasets/{season}/"
    create_dir(season_dir)

    if all_comps:
        season_dir = f"./../../datasets/{season}/All-Competitions/"
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
        team_url_components = team_url.split("/")
        ref_pos = team_url_components.index("squads", 0, len(team_url_components)) + 2
        url_league_id = "all_comps" if all_comps else f"c{league_id}"
        team_url_components = team_url_components[:ref_pos] + [season, url_league_id] + team_url_components[ref_pos:]
        team_url = base_url + "/".join(team_url_components) + f"-{league_name}"
        print(team_name, team_url)
        # time.sleep(5)
        get_team_stats(team_name, team_url, league_dir, league_id, all_comps)


league_name = args.league
season = args.season
all_comps = args.all_comps

get_league_dataset(league_name, season, all_comps)