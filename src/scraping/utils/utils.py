import os
import pandas as pd
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag


class ScrapeArgs:

    def __init__(
        self,
        root_dir: Path = None,
        league_name: str = None,
        season: str = None,
        all_comps: bool = None,
        league_id: str = None,
        league_dir: Path = None,
        team: str = None
    ):
        self.root_dir = root_dir
        self.league_name = league_name
        self.season = season
        self.all_comps = all_comps
        self.league_id = league_id
        self.league_dir = league_dir
        self.team = team


class ScrapeTeamArgs:

    def __init__(
        self,
        team_name: str = None,
        team_url: str = None,
        team_id: str = None,
        team_dir: Path = None,
    ):
        self.team_name = team_name
        self.team_url = team_url
        self.team_id = team_id
        self.team_dir = team_dir



national_tournaments = [676]

'''
list of admissible values for the the league argument
'''
admissible_leagues = [
    "Serie-A",
    "Premier-League",
    "La-Liga",
    "Bundesliga",
    "Ligue-1",
    "Champions-League",
    "European-Championship"
]

league_to_id_map = {
    "Serie-A": 11,
    "Premier-League": 9,
    "La-Liga": 12,
    "Bundesliga": 20,
    "Ligue-1": 13,
    "Champions-League": 8,
    "European-Championship": 676
}

'''

'''
def create_dir(dir_name: Path):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

def create_file(file_path: Path, content: str):
    with open(file_path, "w") as f:
        f.write(content)

'''

'''
def merge_data_frames(df_list, ref_col):
    merged_df = df_list[0]
    for df in df_list[1:]:
        merged_df = pd.merge(merged_df, df, on=ref_col, how='inner', suffixes=('', '_to_drop'))
        merged_df = merged_df[[col for col in merged_df.columns if not col.endswith("_to_drop")]]
    return merged_df    


def check_match_existence(file_path, match_type):
    
    assert match_type in ["fbref", "whoscored"], 'The match_type argument must be "whoscored" or "fbref"'

    if not os.path.exists(file_path):
        return False

    f = open(file_path)
    match_dict = json.load(f)

    if match_dict[match_type] == True:
        return True

    return False


def save_match_info_json_file(file_path, match_type, dict_data):
    
    assert match_type in ["fbref", "whoscored"], 'The match_type argument must be "whoscored" or "fbref"'

    if not os.path.exists(file_path):

        match_dict = {
            "team": dict_data["team"],#team if venue == "home" else opponent,
            "opponent": dict_data["opponent"],#opponent if venue == "home" else team,
            "whoscored": True if match_type == "whoscored" else False,
            "fbref": True if match_type == "fbref" else False,
            "venue": dict_data["venue"],
            "index": dict_data["index"]
        }

        with open(file_path, 'w') as f:
            json.dump(match_dict, f)

    
    f = open(file_path)
    match_dict = json.load(f)

    if match_dict[match_type] == True:
        return
    
    match_dict[match_type] = True
    with open(file_path, 'w') as f:
        json.dump(match_dict, f)


def try_till_it_is_true(function, exception, sleep_time=1):
    while True:
        try:
            function()
            break
        except exception:
            time.sleep(sleep_time)



def get_teams_table(soup: BeautifulSoup, league_id: str) -> ResultSet[Tag]:

    if league_id not in national_tournaments:
        div = soup.select('div[id^="all_results"]')[-1]        
    else:
        div = soup.select('div[id^="all_stats_squads"]')[0]

    table = div.select('table[class^="stats_table"]')[0].select('tbody')[0]
    teams = table.select('tr')

    return teams    


def get_team_url(team, data, matchlogs=False):

    tag = "th" if data.league_id in national_tournaments else "td"
    team_stats = team.select(f"{tag}[data-stat='team']")[0]

    if  len(team_stats.select("a")) == 0:
        return  None

    '''
    extract from the row the id of the team in the fbref database so that we can
    rebuild the url of the team page
    '''
    team_info = team_stats.select("a")[0]
    team_name = team_info.text
    team_url = team_info.get("href")
    url_compontens = team_url.split("/")
    team_id = url_compontens[3]
    league_id_item = "all_comps" if data.all_comps else f"c{data.league_id}"

    if matchlogs:
        team_url = f"https://fbref.com/en/squads/{team_id}/{data.season}/{league_id_item}/matchlogs/Scores-and-Fixtures"
    else:
        team_url = f"https://fbref.com/en/squads/{team_id}/{data.season}/{league_id_item}/Stats"
    
    return team_url, team_name, team_id


'''
Arguments:
- table: the html code of the data table to parse
- team_name: the name of the team of which we want to scrape the data
- all_comps: boolean argument. If it is set to false the function will only download the data realtive
  to the games played in the league. If it is set to true the function will download the data relative
  to the games played in all the competitions of the season
'''
def parse_table(
    table,
    team_name,
    team_id,
    all_comps=False,
    return_opponent=True
):

    # dictionaries which will contains the data of the players, the team and the opponents
    players_stats = {}
    team_stats = {}
    opponent_stats = {}

    '''
    extracting the header of the table (which contains the names of the attributes) and the body of the 
    table that contains the values of the 
    '''
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
    players_stats["team_id"] = []

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
            if return_opponent:
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
            players_stats["team_id"].append(team_id)

            stats = player.select("td")
            for stat in stats:

                stat_text = stat.text

                if stat_text == "Matches":
                    continue

                if stat_text == "":
                    stat_text = None

                attribute = stat.get('data-stat')
                players_stats[attribute].append(stat_text)

    if all_comps:
        return players_stats

    if not all_comps:

        # get team stats
        squad_stats = table_foot.select('tr')[0].select('td')
        team_stats["team"] = [team_name]
        team_stats["team_id"] = [team_id]
        for stat in squad_stats:

            attribute = stat.get('data-stat')
            if attribute in ["nationality", "position", "matches"]:
                continue

            stat_text = stat.text

            if stat_text == "":
                stat_text = None

            
            team_stats[attribute].append(stat_text)

        if return_opponent:
            opp_stats = table_foot.select('tr')[1].select('td')
            opponent_stats["team"] = [team_name]
            opponent_stats["team_id"] = [team_id]
            for stat in opp_stats:

                attribute = stat.get('data-stat')
                if attribute in ["nationality", "position", "matches"]:
                    continue

                stat_text = stat.text

                if stat_text == "":
                    stat_text = None

                opponent_stats[attribute].append(stat_text)

        if return_opponent:
            return players_stats, team_stats, opponent_stats

        return players_stats, team_stats

    return players_stats


# adds the / character at the end of the path if not present
def add_trailing_slash(path):
    return path + ("/" if path[-1] != "/" else "")


def create_league_directory(data: ScrapeArgs) -> Path:

    # data.root_dir = add_trailing_slash(data.root_dir)
    # season_dir = f"{data.root_dir}{data.season}/"
    season_dir = data.root_dir.joinpath(data.season)

    if data.all_comps:
        season_dir = data.root_dir.joinpath("All-Competitions")

    create_dir(season_dir)

    league_dir =  season_dir.joinpath(data.league_name)
    create_dir(league_dir)

    return league_dir

def create_league_url(data : ScrapeArgs) -> str:
    url = f"https://fbref.com/en/comps/{data.league_id}/{data.season}/{data.league_name}-Stats"
    if data.league_id in national_tournaments:
        url = f"https://fbref.com/en/comps/{data.league_id}/{data.season}/stats/{data.season}-{data.league_name}-Stats"
    return url