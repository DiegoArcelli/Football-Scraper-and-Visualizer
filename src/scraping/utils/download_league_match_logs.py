import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
from pyppeteer.errors import TimeoutError, BrowserError
from .utils import *
import time
import os
import re
import copy


'''
Function to read a table of statistics of a given team

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
    all_comps
):

    # dictionaries which will contains the data of the players, the team and the opponents
    players_stats = {}
    team_stats = {}

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

    
        return players_stats, team_stats

    return players_stats



def parse_minute(minute):

    if type(minute) is int:
        return minute

    if "+" not in minute:
        return int(minute)
    
    minute, extra = minute.split("+")
    return int(minute) + int(extra)



def save_match_info(match_info_path, match_id, match_code):
    file_content = f"round,match_id\n{match_id},{match_code}"
    with open(match_info_path, "w") as match_file:
        match_file.write(file_content)

def save_matchlogs_table(file_path, shots_list):
    file_content = "minute,team,player,player_id,scored,xg,xgot,penalty\n"
    for (minute, team, player, player_id, outcome, xg, xgot, penalty) in shots_list:
        file_content += f"{minute},{team},{player},{player_id},{outcome},{xg},{xgot},{penalty}\n"
    
    with open(file_path, "w") as match_file:
        match_file.write(file_content)


def save_game_states(file_path, game_states):
    file_content = "half,start_minute,end_minute,state\n"
    for (half,minute_start, minute_end, state) in game_states:
        file_content += f"{half},{minute_start},{minute_end},{state}\n"
    
    with open(file_path, "w") as match_file:
        match_file.write(file_content)

def save_opponent_info(file_path, opponent_name, opponent_id):
    file_content = f"opponent_name,opponent_id\n{opponent_name},{opponent_id}"
    with open(file_path, "w") as opponent_file:
        opponent_file.write(file_content)


def get_opponent_team_info(soup, venue):
    scorebox = soup.select("div[class='scorebox']")[0]

    idx = 1 if venue == "Home" else 0

    opp_team_info = scorebox.find_all('div', class_=False, recursive=False)[idx].find("strong").find("a")
    opponent_name = opp_team_info.text
    # print(venue, opponent_name)
    opponent_id = opp_team_info.get("href").split("/")[3]

    return opponent_name, opponent_id



def get_match_info_tables(soup, team, team_id, opponent_name, opponent_id, venue):

    tables_names = ["summary", "passing", "passing_types", "defense", "possession", "misc"]

    if venue == "Home":
        team_idx = 0
        opp_idx = 1
    else:
        team_idx = 1
        opp_idx = 0

    
    dataframes = []
    dfs_team_players_stats = []; dfs_opponent_players_stats = []
    dfs_team_stats = []; dfs_opponent_stats = []



    for table in tables_names:
        pattern = re.compile(fr'^stats_.*_{table}$')
        tables = soup.find_all('table', id=pattern)

        home_table = tables[team_idx]
        opp_table = tables[opp_idx]

        team_player_stats, team_stats = parse_table(home_table, team, team_id, False)
        opponent_player_stats, opp_stats = parse_table(opp_table, opponent_name, opponent_id, False)



        dfs_team_players_stats.append(pd.DataFrame.from_dict(team_player_stats))
        dfs_opponent_players_stats.append(pd.DataFrame.from_dict(opponent_player_stats))
        dfs_team_stats.append(pd.DataFrame.from_dict(team_stats))
        dfs_opponent_stats.append(pd.DataFrame.from_dict(opp_stats))

        

    pattern = re.compile(r'^keeper_stats_.*$')
    tables = soup.find_all('table', id=pattern)
    home_table = tables[team_idx]
    opp_table = tables[opp_idx]
    team_gk_stats = parse_table(home_table, team, team_id, True)
    opponent_gk_stats = parse_table(opp_table, opponent_name, opponent_id, True)
    df_team_gk_stats = pd.DataFrame.from_dict(team_gk_stats)
    df_opponent_gk_stats = pd.DataFrame.from_dict(opponent_gk_stats)
    # dataframes.append(("gk", team_player_stats, None, opponent_player_stats, None))

    return dfs_team_players_stats, dfs_opponent_players_stats, dfs_team_stats, dfs_opponent_stats, df_team_gk_stats, df_opponent_gk_stats


def parse_event_panel(soup, venue, first_half_minutes, second_half_minutes):

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


    def is_first_half(minute):
        if "+" not in minute and int(minute) <= 45:
            return True
        if "+" in minute and int(minute.split("+")[0]) <= 45:
            return True
        return False


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

    minutes = [minute for _, minute in goals_minute]
    first_half_max = [minute for minute in minutes if minute[:2] == "45"]
    second_half_max = [minute for minute in minutes if minute[:2] == "90"]
    first_half_max = "45" if first_half_max == [] else first_half_max[-1]
    second_half_max = "90" if second_half_max == [] else second_half_max[-1]
    first_half_minutes = first_half_minutes if parse_minute(first_half_minutes) > parse_minute(first_half_max) else first_half_max
    second_half_minutes = second_half_minutes if parse_minute(second_half_minutes) > parse_minute(second_half_max) else second_half_max
    # full_minutes = second_half_extra + 90
    # exit()

    home_goals, away_goals = 0, 0
    ref_minute = 1
    state = "draw"
    states = []
    first_half = True

    # print(goals_minute)

    for team, minute in goals_minute:
        if first_half and not is_first_half(minute):
            if states == []:
                states.append(("first", ref_minute, first_half_minutes, state))
            else:
                _, old_start, old_end, old_state = states[-1]
                states.append(("first", old_end, first_half_minutes, new_state))
                # states.append((old_end, first_half_minutes, old_state))
            first_half = False
            ref_minute = "46"


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
            states.append(("first" if first_half else "second", ref_minute, minute, state))
            state = new_state
            ref_minute = minute
        
    #minutes_in_state = full_minutes - ref_minute
    _, last_start, last_end, last_state = states[-1]
    # case in which there have been no goals in the second half
    if is_first_half(ref_minute):
        states.append(("first", last_end, first_half_minutes, state))
        ref_minute = "46"
    states.append(("second", ref_minute, second_half_minutes, state))
        
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

    minutes = list(map(lambda x: x[0], match_shots_info))
    first_half_minute = [minute for minute in minutes if minute[:2] == "45"]
    second_half_minute = [minute for minute in minutes if minute[:2] == "90"]
    first_half_minutes = "45" if first_half_minute == [] else first_half_minute[-1]
    second_half_minutes = "90" if second_half_minute == [] else second_half_minute[-1]

    game_states = parse_event_panel(soup, venue, first_half_minutes, second_half_minutes)

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
    matches = match_table.select('tr')[1:]

    match_id = 1
    base_url = "https://fbref.com"

    # for match in matches:
    #     print(match)
    # exit()

    for match in matches:

        match_dir = f"{team_dir}match_{match_id}/"

        match_file_path = f"{match_dir}shots.csv"
        state_file_path = f"{match_dir}game_states.csv"
        opponent_file_path = f"{match_dir}opponent_info.csv"
        match_info_path = f"{match_dir}match_info.csv"
        
        if os.path.exists(opponent_file_path): # and os.path.exists(match_file_path):
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

        is_page_dowloaded = False
        while not is_page_dowloaded:
            try:
                r = session.get(match_url)
                r.html.render()  # this call executes the js in the page
                is_page_dowloaded = True
            except (TimeoutError, BrowserError):
                print("Retrying download")
                is_page_dowloaded = False 
                
        html_content = r.html.html
        match_soup = BeautifulSoup(html_content, 'html.parser')

        match_code = match_url.split("/")[5]

        opponent_name, opponent_id = get_opponent_team_info(match_soup, venue)


        match_shots, game_states = parse_shooting_table(match_soup, team_id, venue)
        dataframes = get_match_info_tables(match_soup, team, team_id, opponent_name, opponent_id, venue)
        team_players_stats, opponent_players_stats, team_stats, opponent_stats, team_gk_stats, opponent_gk_stats = dataframes
        
        team_players_stats = merge_data_frames(team_players_stats, "player_id")
        opponent_players_stats = merge_data_frames(opponent_players_stats, "player_id")
        team_stats = merge_data_frames(team_stats, "team")
        opponent_stats = merge_data_frames(opponent_stats, "team")

        team_stats.drop(['shirtnumber', 'age'], axis=1, inplace=True)
        opponent_stats.drop(['shirtnumber', 'age'], axis=1, inplace=True)

        create_dir(match_dir)

        # table, team_player_stats, team_stats, opponent_player_stats, opp_stats

        team_players_stats.to_csv(f"{match_dir}team_players_stats.csv", index=False)
        opponent_players_stats.to_csv(f"{match_dir}opponent_players_stats.csv", index=False)
        team_stats.to_csv(f"{match_dir}team_stats.csv", index=False)
        opponent_stats.to_csv(f"{match_dir}opponent_stats.csv", index=False)
        team_gk_stats.to_csv(f"{match_dir}team_gk_stats.csv", index=False)
        opponent_gk_stats.to_csv(f"{match_dir}opponent_gk_stats.csv", index=False)
        save_matchlogs_table(match_file_path, match_shots)
        save_game_states(state_file_path, game_states)
        save_match_info(match_info_path, match_id, match_code)
        save_opponent_info(opponent_file_path, opponent_name, opponent_id)

        match_id += 1
        time.sleep(3)
        
        

    # players_df = merge_data_frames(players_tables, "player_id")
    # gk_df = merge_data_frames(gk_tables, "player_id")
    # players_df.to_csv(f"{team_dir}/players.csv", index=False)
    # gk_df.to_csv(f"{team_dir}/goalkeepers.csv", index=False)

    # if not all_comps:
    #     team_df = merge_data_frames(team_tables, "team")
    #     opponent_df = merge_data_frames(opponent_table, "team")
    #     team_df.to_csv(f"{team_dir}/team.csv", index=False)
    #     opponent_df.to_csv(f"{team_dir}/opponents.csv", index=False)

'''
function to download the match logs of every team of a given league.
'''
def get_league_match_logs(
        root_dir : str = "./../../datasets/",
        league_name : str = "Serie-A",
        season : str = "2023-2024", 
        all_comps : bool = False
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
        print("\n")