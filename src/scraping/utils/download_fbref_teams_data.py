from bs4 import BeautifulSoup
import pandas as pd
from .utils import *
import time
from selenium import webdriver



def get_goalkeepers_data(
    soup,
    team_data,
    data,
    tables
):
    gk_table_names = [
        f"stats_keeper_{data.league_id}",
        f"stats_keeper_adv_{data.league_id}"
    ]

    for gk_table_name in gk_table_names:
        table = soup.select(f"table#{gk_table_name}")[0]

        if not data.all_comps:
            gk_stats, team_stats, opponent_stats = parse_table(table, team_data.team_name, team_data.team_id, data.all_comps, True)
            gk_df = pd.DataFrame.from_dict(gk_stats)
            team_df = pd.DataFrame.from_dict(team_stats)
            opponent_df = pd.DataFrame.from_dict(opponent_stats)

            tables["gk_tables"].append(gk_df)
            tables["team_tables"].append(team_df)
            tables["opponent_tables"].append(opponent_df)
        else:
            gk_stats = parse_table(table, team_data.team_name, team_data.team_id, data.all_comps, True)
            gk_df = pd.DataFrame.from_dict(gk_stats)
            tables["gk_tables"].append(gk_df)


def get_players_data(
    soup,
    team_data,
    data,
    tables,
):
    
    table_names = [
        f"stats_standard_{data.league_id}",
        f"stats_shooting_{data.league_id}",
        f"stats_passing_{data.league_id}",
        f"stats_passing_types_{data.league_id}",
        f"stats_gca_{data.league_id}",
        f"stats_defense_{data.league_id}",
        f"stats_possession_{data.league_id}",
        f"stats_playing_time_{data.league_id}",
        f"stats_misc_{data.league_id}"
    ]
    
    for table_name in table_names:
        # print(f"table#{table_name}")
        table = soup.select(f"table#{table_name}")[0]

        if not data.all_comps:
            players_stats, team_stats, opponent_stats = parse_table(table, team_data.team_name, team_data.team_id, data.all_comps, True)
            players_df = pd.DataFrame.from_dict(players_stats)
            team_df = pd.DataFrame.from_dict(team_stats)
            opponent_df = pd.DataFrame.from_dict(opponent_stats)
            tables["players_tables"].append(players_df)
            tables["team_tables"].append(team_df)
            tables["opponent_tables"].append(opponent_df)
        else:
            players_stats = parse_table(table, team_data.team_name, team_data.team_id, data.all_comps, True)
            players_df = pd.DataFrame.from_dict(players_stats)
            tables["players_tables"].append(players_df)


def save_data(data, team_data, tables):
    print(f"Saving {team_data.team_name} data in {team_data.team_dir}")
    players_df = merge_data_frames(tables["players_tables"], "player_id")
    gk_df = merge_data_frames(tables["gk_tables"], "player_id")
    players_df.to_csv(f"{team_data.team_dir}/players.csv", index=False)
    gk_df.to_csv(f"{team_data.team_dir}/goalkeepers.csv", index=False)

    if not data.all_comps:
        team_df = merge_data_frames(tables["team_tables"], "team")
        opponent_df = merge_data_frames(tables["opponent_tables"], "team")
        team_df.to_csv(f"{team_data.team_dir}/team.csv", index=False)
        opponent_df.to_csv(f"{team_data.team_dir}/opponents.csv", index=False)


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
        team_data,
        data
    ) -> None:

    # creation of the directory for the specific team
    team_dir = f"{data.league_dir}{team_data.team_name}/"
    team_data.team_dir = team_dir
    create_dir(team_data.team_dir)
    
    driver.get(team_data.team_url)

    while True:
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        if len(soup.select(f"table#stats_standard_{data.league_id}")) > 0:
            break
        else:
            time.sleep(1)

    if data.all_comps:
        table = soup.select("table#stats_standard_combined")
        if len(table) > 0:
            data.league_id = "combined"
        else:
            data.all_comps = False
    
    tables = {
        "players_tables": [],
        "gk_tables": [],
        "team_tables": [],
        "opponent_tables": []
    }

    get_players_data(soup, team_data, data, tables)
    get_goalkeepers_data(soup, team_data, data, tables)
    save_data(data, team_data, tables)

def create_league_team_names_file(teams, data):
    teams_name_path = f"{data.league_dir}fbref_names.txt"

    if os.path.exists(teams_name_path):
        return 
    
    team_names = [get_team_url(team, data, False)[1] for team in teams]
    team_names = sorted(team_names)
    file_content = "\n".join(team_names)
    with open(teams_name_path, "w") as f:
        f.write(file_content)



def scrape_teams_data(driver, teams, data):
    for team in teams:
        
        output = get_team_url(team, data, False)
        if output is None:
            continue

        team_url, team_name, team_id = output

        team_data = ScrapeTeamArgs(
            team_name=team_name,
            team_url=team_url,
            team_id=team_id
        )

        print(f"\n{team_url}")

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        get_team_data(driver, team_data, data)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])      
        time.sleep(3)



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
def get_league_data(data : ScrapeArgs) -> None:


    assert data.league_name in admissible_leagues, f"Not valid league name. Valid names are {admissible_leagues}"


    # set up the directories structure on which to download the files   
    data.league_dir = create_league_directory(data)

    # get the id of the league of which to download the data 
    data.league_id = league_to_id_map[data.league_name]

    # definition of the fbref url containing the data of the league
    url = create_league_url(data)

    print(f"Downloading {data.league_name} {data.season} data")
    print(url)

    driver = webdriver.Chrome()
    driver.get(url)
    html_content = driver.page_source
    # driver.close()

    soup = BeautifulSoup(html_content, 'html.parser')

    # we extract from the html page of the the table containing a list of all the teams of the league
    teams = get_teams_table(soup, data.league_id)  

    create_league_team_names_file(teams, data)

    # iterate through each row of the table
    scrape_teams_data(driver, teams, data)
    
    driver.close()