import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
from pyppeteer.errors import TimeoutError, BrowserError
from .utils import *
import time
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

'''
Function to extract data of a given team

Arguments:
- team: the name of the team of which we want to scrape the data
- team_url: the url of the fbref webpage of the team
- league_dir: the path of the directory that contains the data of the league
- league_id: the id of the league to which the team belongs
- all_comps: boolean argument. If it is set to false the function will only download the data realtive
  to the games played in the league. If it is set to true the function will download the data relative
  to the games played in all the competitions of the season
'''
def get_team_data(
        driver,
        team : str,
        team_id : str,
        team_url : str, 
        league_dir : str,
        league_id : int,
        all_comps : bool
    ) -> None:

    # creation of the directory for the specific team
    team_dir = f"{league_dir}{dir_name}/"
    create_dir(team_dir)
    driver.get(team_url)

    while True:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        if len(soup.select(f"table#stats_standard_{league_id}")) > 0:
            break
        else:
            time.sleep(1)

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
            players_stats, team_stats, opponent_stats = parse_table(table, team, team_id, all_comps, True)
            players_df = pd.DataFrame.from_dict(players_stats)
            team_df = pd.DataFrame.from_dict(team_stats)
            opponent_df = pd.DataFrame.from_dict(opponent_stats)
            players_tables.append(players_df)
            team_tables.append(team_df)
            opponent_table.append(opponent_df)
        else:
            players_stats = parse_table(table, team, team_id, all_comps, True)
            players_df = pd.DataFrame.from_dict(players_stats)
            players_tables.append(players_df)


    for gk_table_name in gk_tables_names:
        table = soup.select(f"table#{gk_table_name}")[0]

        if not all_comps:
            gk_stats, team_stats, opponent_stats = parse_table(table, team, team_id, all_comps, True)
            gk_df = pd.DataFrame.from_dict(gk_stats)
            team_df = pd.DataFrame.from_dict(team_stats)
            opponent_df = pd.DataFrame.from_dict(opponent_stats)

            gk_tables.append(gk_df)
            team_tables.append(team_df)
            opponent_table.append(opponent_df)
        else:
            gk_stats = parse_table(table, team, team_id, all_comps, True)
            gk_df = pd.DataFrame.from_dict(gk_stats)
            gk_tables.append(gk_df)

    print(f"Saving {team} data in {team_dir}")
    players_df = merge_data_frames(players_tables, "player_id")
    gk_df = merge_data_frames(gk_tables, "player_id")
    players_df.to_csv(f"{team_dir}/players.csv", index=False)
    gk_df.to_csv(f"{team_dir}/goalkeepers.csv", index=False)

    if not all_comps:
        team_df = merge_data_frames(team_tables, "team")
        opponent_df = merge_data_frames(opponent_table, "team")
        team_df.to_csv(f"{team_dir}/team.csv", index=False)
        opponent_df.to_csv(f"{team_dir}/opponents.csv", index=False)



'''
Function to donwload the seasonal data of a team and its players

Arguments:
- root_dir: path to the directory on which to download the data
- league_name: name of the league of which we want to download the data. The possible values for this argument
  are in the variable `admissible_leagues`
- season: season of which we want to download the data. It has to be a string of the form: "{x}-{x+1}" where x is an integer number
- all_comps: boolean argument. If it is set to false the function will only download the data realtive
  to the games played in the league. If it is set to true the function will download the data relative
  to the games played in all the competitions of the season

Output:
the data are donwloaded in root_dir the structure of the directories inside root_dir will
be the follwing if all_comps is False:
root_dir/
    season/
        league/
            team_name/
                team.csv
                players.csv
                opponents.csv
                goalkeepers.csv
        team.csv
        players.csv
        opponents.csv
        goalkeepers.csv
    team.csv
    players.csv
    opponents.csv
    goalkeepers.csv
            

Otherwise if the all_comps argument is True:
root_dir/
    season/
        All-Competitions/
            league/
                team_name/
                    team.csv
                    players.csv
                    opponents.csv
                    goalkeepers.csv
            team.csv
            players.csv
            opponents.csv
            goalkeepers.csv
        team.csv
        players.csv
        opponents.csv
        goalkeepers.csv
'''
def get_league_data(
    root_dir : str = "./../../datasets/",
    league_name : str = "Serie-A",
    season : str = "2023-2024", 
    all_comps : bool = False) -> None:


    assert league_name in admissible_leagues, f"Not valid league name. Valid names are {admissible_leagues}"

    # set up the directories structure on which to download the files
    root_dir = root_dir + ("/" if root_dir[-1] != "/" else "")
    season_dir = f"{root_dir}{season}/"
    create_dir(season_dir)

    if all_comps:
        season_dir = f"./../../datasets/{season}/All-Competitions/"
        create_dir(season_dir)

    league_dir = f"{season_dir}{league_name}/"
    create_dir(league_dir)

    # get the id of the league of which to download the data 
    league_id = league_to_id_map[league_name]

    # definition of the fbref url containing the data of the league
    base_url = "https://fbref.com"
    url = f"https://fbref.com/en/comps/{league_id}/{season}/{league_name}-Stats"


    if league_id in national_tournaments:
        url = f"https://fbref.com/en/comps/{league_id}/{season}/stats/{season}-{league_name}-Stats"

    print(f"Downloading {league_name} {season} data")
    print(url)

    driver = webdriver.Chrome()
    driver.get(url)
    html_content = driver.page_source
    # driver.close()

    # we extract from the html page of the the table containing a list of all the teams of the league
    soup = BeautifulSoup(html_content, 'html.parser')
    teams = get_teams_table(soup, league_id)  

    teams_name_path = f"{league_dir}fbref_names.txt"
    if not os.path.exists(teams_name_path):
        team_names = [get_team_url(team, league_id, season, all_comps, False)[1] for team in teams]
        team_names = sorted(team_names)
        file_content = "\n".join(team_names)
        with open(teams_name_path, "w") as f:
            f.write(file_content)


    # for team in teams:
    #     _, team_name, _ = get_team_url(team, league_id, season, all_comps, False)
    # iterate through each row of the table
    for team in teams:
        
        output = get_team_url(team, league_id, season, all_comps, False)
        if output is None:
            continue

        team_url, team_name, team_id = output
        print(f"\n{team_url}")

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        get_team_data(driver, team_name, team_id, team_url, league_dir, league_id, all_comps)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])      
        time.sleep(3)
    
    driver.close()
