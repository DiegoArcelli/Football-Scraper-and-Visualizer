from bs4 import BeautifulSoup
import pandas as pd
from .utils import *
import time
import os
import re
from selenium import webdriver

def parse_minute(minute):

    if type(minute) is int:
        return minute

    if "+" not in minute:
        return int(minute)
    
    minute, extra = minute.split("+")
    return int(minute) + int(extra)



def save_match_info(match_info_path, match_id, matchweek, match_code):
    file_content = f"round,matchweek,match_id\n{match_id},{matchweek},{match_code}"
    with open(match_info_path, "w") as match_file:
        match_file.write(file_content)

def save_matchlogs_table(file_path, shots_list):
    file_content = "minute,team_id,team_name,player,player_id,scored,xg,xgot,penalty\n"
    for (minute, team_id, team_name, player, player_id, outcome, xg, xgot, penalty) in shots_list:
        file_content += f"{minute},{team_id},{team_name},{player},{player_id},{outcome},{xg},{xgot},{penalty}\n"
    
    with open(file_path, "w") as match_file:
        match_file.write(file_content)


def save_game_states(file_path, game_states):
    file_content = "half,start_minute,end_minute,state\n"
    for (half,minute_start, minute_end, state) in game_states:
        file_content += f"{half},{minute_start},{minute_end},{state}\n"
    
    with open(file_path, "w") as match_file:
        match_file.write(file_content)

def save_opponent_info(file_path, opponent_name, opponent_id):
    file_content = f"away_team_name,away_team_id\n{opponent_name},{opponent_id}"
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

        team_player_stats, team_stats = parse_table(home_table, team, team_id, False, False)
        opponent_player_stats, opp_stats = parse_table(opp_table, opponent_name, opponent_id, False, False)



        dfs_team_players_stats.append(pd.DataFrame.from_dict(team_player_stats))
        dfs_opponent_players_stats.append(pd.DataFrame.from_dict(opponent_player_stats))
        dfs_team_stats.append(pd.DataFrame.from_dict(team_stats))
        dfs_opponent_stats.append(pd.DataFrame.from_dict(opp_stats))

        

    pattern = re.compile(r'^keeper_stats_.*$')
    tables = soup.find_all('table', id=pattern)
    home_table = tables[team_idx]
    opp_table = tables[opp_idx]
    team_gk_stats = parse_table(home_table, team, team_id, True, False)
    opponent_gk_stats = parse_table(opp_table, opponent_name, opponent_id, True, False)
    df_team_gk_stats = pd.DataFrame.from_dict(team_gk_stats)
    df_opponent_gk_stats = pd.DataFrame.from_dict(opponent_gk_stats)
    # dataframes.append(("gk", team_player_stats, None, opponent_player_stats, None))

    return dfs_team_players_stats, dfs_opponent_players_stats, dfs_team_stats, dfs_opponent_stats, df_team_gk_stats, df_opponent_gk_stats

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



def parse_shooting_table(soup, venue):

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
        shot_team_name = shot_info.select('td[data-stat="team"]')[0].select("a")[0].text

        match_shots_info.append((minute, shot_team_id, shot_team_name, player_name, shot_player_id, outcome, xg, xgot, penalty))

    # minutes = list(map(lambda x: x[0], match_shots_info))
    # first_half_minute = [minute for minute in minutes if minute[:2] == "45"]
    # second_half_minute = [minute for minute in minutes if minute[:2] == "90"]
    # first_half_minutes = "45" if first_half_minute == [] else first_half_minute[-1]
    # second_half_minutes = "90" if second_half_minute == [] else second_half_minute[-1]

    game_states = parse_event_panel(soup, venue)

    return match_shots_info, game_states
    

def parse_match_table(driver, team_data, data):

    # if team not in ["Inter", "Genoa"]:
    #     return


    team_dir = f"{data.league_dir}{team_data.team_name}/"
    create_dir(team_dir)
    team_dir = f"{team_dir}matchlogs/"
    create_dir(team_dir)

    # driver = webdriver.Chrome()
    driver.get(team_data.team_url)
    html_content = driver.page_source
    # driver.close()

    soup = BeautifulSoup(html_content, 'html.parser')

    match_table = soup.select('table[id^="matchlogs"]')[0]
    matches = match_table.select('tr')[1:]

    match_id = 1
    base_url = "https://fbref.com"

    # for match in matches:
    #     print(match)
    # exit()

    matches = [match for match in matches if match.select('td[data-stat="match_report"]') != []]

    create_dir(f"{data.league_dir}matches/")

    for match in matches:


        match_cell = match.select('td[data-stat="match_report"]')
        if match_cell == []:
            continue

        match_report = match_cell[0].select("a")[0].text
        # match_report = match.select('td[data-stat="match_report"]')[0].select("a")[0].text
        # # print(match_report)
        if match_report != "Match Report":
            continue


        match_url = match_cell[0].select('a')

        if match_url == []:
            continue

        opponent = match.select('td[data-stat="opponent"]')[0].text
        venue = match.select('td[data-stat="venue"]')[0].text.lower()

        match_dict = {
            "team": team_data.team_name if venue == "home" else opponent,
            "opponent": opponent if venue == "home" else team_data.team_name,
            "venue": venue,
            "index": match_id
        }

        match_file = f"{team_dir}match_{match_id}.json"
        print(match_file)
        if check_match_existence(match_file, "fbref"):
            save_match_info_json_file(match_file, "fbref", match_dict)
            match_id += 1
            continue

        match_name = f'{team_data.team_name}-{opponent}' if venue == "home" else f'{opponent}-{team_data.team_name}'
        match_dir = f"{data.league_dir}matches/{match_name}/"
        create_dir(match_dir)

        # if os.path.exists(match_dir + "match_info.json"):
        #     match_id += 1
        #     continue

        match_file_path = f"{match_dir}shots.csv"
        state_file_path = f"{match_dir}game_states.csv"
        opponent_file_path = f"{match_dir}away_team_info.csv"
        match_info_path = f"{match_dir}match_info.csv"
        
        print(opponent_file_path)
        if os.path.exists(opponent_file_path): # and os.path.exists(match_file_path):
            save_match_info_json_file(match_file, "fbref", match_dict)
            match_id += 1
            continue

        match_url= match_url[0].get("href")
        match_url = f"{base_url}{match_url}"

        matchweek = match.select('td[data-stat="round"]')[0].text
        matchweek = matchweek.split(" ")[-1]

        print(match_url)

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(match_url)

        while True:
            match_soup = BeautifulSoup(html_content, 'html.parser')
            html_content = driver.page_source
            if len(match_soup.select('table[id="shots_all"]')) > 0:
                break
            else:
                time.sleep(1)


        match_code = match_url.split("/")[5]

        opponent_name, opponent_id = get_opponent_team_info(match_soup, venue)


        match_shots, game_states = parse_shooting_table(match_soup, venue)
        dataframes = get_match_info_tables(match_soup, team_data.team_name, team_data.team_id, opponent_name, opponent_id, venue)
        team_players_stats, opponent_players_stats, team_stats, opponent_stats, team_gk_stats, opponent_gk_stats = dataframes
        
        team_players_stats = merge_data_frames(team_players_stats, "player_id")
        opponent_players_stats = merge_data_frames(opponent_players_stats, "player_id")
        team_stats = merge_data_frames(team_stats, "team")
        opponent_stats = merge_data_frames(opponent_stats, "team")

        team_stats.drop(['shirtnumber', 'age'], axis=1, inplace=True)
        opponent_stats.drop(['shirtnumber', 'age'], axis=1, inplace=True)

        # table, team_player_stats, team_stats, opponent_player_stats, opp_stats
        reference_team = venue
        opponent_team = "away" if venue == "home" else "home"
        

        team_players_stats.to_csv(f"{match_dir}{reference_team}_team_players_stats.csv", index=False)
        opponent_players_stats.to_csv(f"{match_dir}{opponent_team}_team_players_stats.csv", index=False)
        team_stats.to_csv(f"{match_dir}{reference_team}_team_stats.csv", index=False)
        opponent_stats.to_csv(f"{match_dir}{opponent_team}_team_stats.csv", index=False)
        team_gk_stats.to_csv(f"{match_dir}{reference_team}_gk_stats.csv", index=False)
        opponent_gk_stats.to_csv(f"{match_dir}{opponent_team}_gk_stats.csv", index=False)
        save_matchlogs_table(match_file_path, match_shots)
        save_game_states(state_file_path, game_states)
        save_match_info(match_info_path, match_id, matchweek, match_code)
        save_opponent_info(opponent_file_path, opponent_name, opponent_id)

        driver.close()
        driver.switch_to.window(driver.window_handles[-1])

        save_match_info_json_file(match_file, "fbref", match_dict)


        match_id += 1
        time.sleep(1)
        
        

    # players_df = merge_data_frames(players_tables, "player_id")
    # gk_df = merge_data_frames(gk_tables, "player_id")
    # players_df.to_csv(f"{team_dir}/players.csv", index=False)
    # gk_df.to_csv(f"{team_dir}/goalkeepers.csv", index=False)

    # if not all_comps:
    #     team_df = merge_data_frames(team_tables, "team")
    #     opponent_df = merge_data_frames(opponent_table, "team")
    #     team_df.to_csv(f"{team_dir}/team.csv", index=False)
    #     opponent_df.to_csv(f"{team_dir}/opponents.csv", index=False)


def scrape_teams_data(driver, teams, data):
    ref_team = data.team
    for team in teams:

        output = get_team_url(team, data, True)
        
        if output is None:
            continue

        team_url, team_name, team_id = output

        team_data = ScrapeTeamArgs(
            team_url=team_url,
            team_name=team_name,
            team_id=team_id
        )

        if ref_team is not None and team_name != ref_team:
            continue

        print(f"\n{team_url}")
        time.sleep(1)

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        parse_match_table(driver, team_data, data)

        driver.close()
        driver.switch_to.window(driver.window_handles[0])


'''
function to download the match logs of every team of a given league.
'''
def get_league_match_logs(data : ScrapeArgs) -> None:

    
    data.league_dir = create_league_directory(data)
    data.league_id = league_to_id_map[data.league_name]

    url = create_league_url(data)
    print(url)

    driver = webdriver.Chrome()
    driver.get(url)
    html_content = driver.page_source
    # driver.close()


    soup = BeautifulSoup(html_content, 'html.parser')
    teams = get_teams_table(soup, data.league_id)


    scrape_teams_data(driver, teams, data)

    driver.close()