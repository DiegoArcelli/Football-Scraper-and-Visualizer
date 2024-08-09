import json
import chompjs
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import os


# actions = ActionChains(driver)
# html_content = driver.page_source


def assign(data, key):
    try:
        return data[key]
    except KeyError:
        return None


def extract_match_panel_info(data_dir, html_content):
    info = html_content.split("require.config.params['matchheader'] = ")[1].split(";")[0].replace("\n", " ")
    info_list = info.split("[")[1].split("]")[0].split(",")
    match_id = info.replace(" ", "").split("matchId:")[1].split("}")[0]

    match_info = {}

    input_list = []
    for element in info_list:
        val = element
        if element == "":
            val = None
        elif element[0] == "'" and element[-1] == "'":
            val = element[1:-1]
        input_list.append(val)

    match_info["input"] = input_list
    match_info["match_id"] = match_id

    id_to_team_map = {
        input_list[0]: input_list[2],
        input_list[1]: input_list[3]
    } 

    # # Isolate the JSON part from the script content
    json_str = html_content.split('require.config.params["args"] =')[1].rsplit(';', 1)[0]
    # print(json_str)
    # # Parse the JSON string into a Python dictionary
    data  = chompjs.parse_js_object(json_str)
    # print(data.keys())
    # print(data["matchCentreData"].keys())
    events_type_to_id = data["matchCentreEventTypeJson"]
    events_id_to_type = {value: key for key, value in events_type_to_id.items()}

    players_mapping = data["matchCentreData"]["playerIdNameDictionary"]


    # for event_type in event_types:
    #     print(event_type + ":", data["matchCentreEventTypeJson"][event_type])
    # print()

    events = data["matchCentreData"]["events"]

    attributes = [
        "_id",
        "event_id",
        "minute",
        "second",
        "team_id",
        "team_name",
        "player_id",
        "player_name",
        "x",
        "y",
        "expanded_minute",
        "period",
        "period_value",
        "_type",
        "type_value",
        "is_touch",
        "end_x",
        "end_y",
        "outcome_type",
        "outcome_value",
        "qualifiers",
        "satisfied_events",
        "related_event_id",
        "is_shot",
        "is_goal",
        "goal_mouth_y",
        "goal_mouth_z",
        "blocked_x",
        "blocked_y"
    ]

    dict_df = {attribute: [] for attribute in attributes}

    all_keys = set()
    # print(players_mapping)
    for idx, event in enumerate(events):
        # print(f"Event {idx}")
        _id = assign(event, "id")
        event_id = assign(event, "eventId")
        minute = assign(event, "minute")
        second = assign(event, "second")
        team_id = assign(event, "teamId")
        team_id = str(team_id)
        team_name = id_to_team_map[team_id] if team_id is not None else None
        player_id = assign(event, "playerId")
        player_name = players_mapping[str(player_id)] if player_id is not None else None
        x = assign(event, "x")
        y = assign(event, "y")
        expanded_minute = assign(event, "expandedMinute")
        period = assign(event['period'], "displayName")
        period_value = assign(event['period'], "value")
        _type = assign(event["type"], "displayName")
        type_value = assign(event["type"], "value")
        is_touch = assign(event, "isTouch")
        end_x = assign(event, "endX")
        end_y = assign(event, "endY")
        outcome_type = assign(event["outcomeType"], "displayName")
        outcome_value = assign(event["outcomeType"], "value")
        qualifiers = assign(event, "qualifiers")
        qualifiers = str(qualifiers) if qualifiers is not None else None
        satisfied_events = assign(event, "satisfiedEventsTypes")
        satisfied_events = str([{"event_type_id": event_id, "event_type": events_id_to_type[event_id]} for event_id in satisfied_events])
        related_event_id = assign(event, "relatedEventId")
        is_shot = assign(event, "isShot")
        is_goal = assign(event, "isGoal")
        goal_mouth_y = assign(event, "goalMouthY")
        goal_mouth_z = assign(event, "goalMouthZ")
        blocked_x = assign(event, "blockedX")
        blocked_y = assign(event, "blockedY")

        for attribute in attributes:
            dict_df[attribute].append(locals()[attribute])

        # for key in event.keys():
        #     all_keys.add(key)
        # print("")

    dict_df["type"] = dict_df["_type"]
    dict_df["id"] = dict_df["_id"]
    del dict_df["_type"]
    del dict_df["_id"]
    # print(dict_df)
    file_match_path = data_dir + "match_events.csv"
    match_df = pd.DataFrame.from_dict(dict_df)
    match_df.to_csv(file_match_path, index=False)


    period_ends = match_centre["periodEndMinutes"]

    preiords = {}
    periods["first_half"] = period_ends["1"]
    periods["second_half"] = period_ends["2"]

    file_period_path = data_dir + "preiods.json"

    if "3" in period_ends.keys():
        periods["first_half_overtime"] = period_ends["3"]
    
    if "4" in periods_ends.keys():
        periods["second_half_overtime"] = period_ends["4"]

    with open(f"file_period_path", 'w') as f:
        json.dump(period_ends, f)

    # print(match_df.head(10))


def fix_team_name(team_name):

    if "\n" not in team_name:
        return team_name
    
    team_name = team_name.split("\n")[0]
    return team_name


def get_url(data, league):

    regions_to_league = {
        "Serie-A": "Italy",
        "La-Liga": "Spain",
        "Bundesliga": "Germany",
        "Ligue-1": "France",
        "Premier-League": "England"
    }


    league_to_name = {
        "Serie-A": "Serie A",
        "La-Liga": "LaLiga",
        "Bundesliga": "Bundesliga",
        "Ligue-1": "Ligue 1",
        "Premier-League": "Premier League"
    }

    league_region = regions_to_league[league]
    league = league_to_name[league]

    url = None
    print(league_region, league)
    for region_dict in data:
        region = region_dict["name"]
        if league_region == region:
            tournaments = region_dict["tournaments"]
            for tournament in tournaments:
                if tournament["name"] == league:
                    url = tournament["url"]

    url = "https://www.whoscored.com" + url
    return url, league


def parse(
        root_dir,
        league_name,
        season,
    ):

    f = open("selenium_test/regions.json") 
    data = json.load(f)
    
    url, league = get_url(data, league_name)

    data_dir = f"{root_dir}{season}/{league_name}/"
    # print(url)
    # return
    # url = "https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/9659/Stages/22143/Fixtures/Italy-Serie-A-2023-2024"
    # url = "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A"
    driver = webdriver.Chrome()
    driver.get(url)

    driver.find_element(By.XPATH, "//button[contains(@class, 'css-1wc0q5e')]").click()
    print("Accepted cookies")
    print(driver.title)

    driver.find_element(By.CSS_SELECTOR, "div[id='sub-navigation']").find_elements(By.CSS_SELECTOR, "li")[1].click()
    print(driver.title)

    def select(xpath, value):
        curr_value = driver.find_element(By.XPATH, xpath)
        curr_value = Select(curr_value).first_selected_option.text
        # print(curr_value, value)
        while value != curr_value:
            value_menu = driver.find_element(By.XPATH, xpath)
            select = Select(value_menu)
            select.select_by_visible_text(value)
            curr_value = Select(driver.find_element(By.XPATH, xpath)).first_selected_option.text
            # print(curr_value, value)
            time.sleep(3)


    season = season.replace("-", "/")
    select("//select[contains(@id, 'season')]", season)
    select("//select[contains(@id, 'tournaments')]", league)
    # select("//select[contains(@id, 'locale-select')]", "EN")


    # select(driver, "//select[contains(@id, 'season')]", "2021/2022")

    # season = "2023/2024"
    # curr_season = driver.find_element(By.XPATH, "//select[contains(@id, 'season')]")
    # curr_season = Select(curr_season).first_selected_option.text

    # while season != curr_season:
    #     season_menu = driver.find_element(By.XPATH, "//select[contains(@id, 'season')]")
    #     select = Select(season_menu)
    #     select.select_by_visible_text(season)
    #     curr_season = Select(driver.find_element(By.XPATH, "//select[contains(@id, 'season')]")).first_selected_option.text
    #     time.sleep(3)

    teams_games = {}

    old_game = None
    total_games = 0

    count = 0
    while True:
        
        count += 1
        time.sleep(2)
        games = driver.find_elements(By.CSS_SELECTOR, "div[class^='Match-module_match']")
        new_game = games[-1].find_element(By.CSS_SELECTOR, "a[class^='Match-module_stat']").get_attribute("href")
        
        if count == 5:
            break
        
        if new_game == old_game:
            continue

        games = driver.find_elements(By.CSS_SELECTOR, "div[class^='Match-module_match']")

        count = 0
        old_game = new_game
        new_date = driver.find_element(By.CSS_SELECTOR, "span[class='toggleDatePicker']").text

        for game in games[::-1]:
            a_tag = game.find_element(By.CSS_SELECTOR, "a[class^='Match-module_stat']")
            game_url = a_tag.get_attribute("href")
            teams = game.find_elements(By.CSS_SELECTOR, "div[class^='Match-module_teamName']")
            # actions.key_down(Keys.CONTROL).click(a_tag).key_up(Keys.CONTROL).perform()
            # driver.switch_to.window(driver.window_handles[-1])
            # print(driver.current_url)
            # extract_match_panel_info(driver.page_source)
            # driver.close()
            # driver.switch_to.window(driver.window_handles[0])
            # print(driver.current_url)
            
            home, away = fix_team_name(teams[0].text), fix_team_name(teams[1].text)
            
            for team in [home, away]:
                if team in teams_games.keys():
                    teams_games[team].append(game_url)
                else:
                    teams_games[team] = [game_url]

            


        # print(new_date)
        total_games += len(games)
        print(total_games)

        driver.find_element(By.ID, "dayChangeBtn-prev").click()
        # time.sleep(10)
            
    driver.close()

    print(data_dir)
    print(teams_games.keys())
    for team in teams_games.keys():
        print(team, len(teams_games[team]))
        continue
        for idx, game in enumerate(teams_games[team][::-1]):
            print(game)
            data_dir = f"{data_dir}{team}/matchlogs/match_{idx+1}/"
            if not os.path.exists(data_dir):
                driver = webdriver.Chrome()
                driver.get(game)
                extract_match_panel_info(data_dir, driver.page_source)
                driver.close()
                print(f"Saved data in {data_dir}")
        print("")

    # for game in teams_games["Juventus"][::-1]:
    #     driver = webdriver.Chrome()
    #     driver.get(game)
    #     extract_match_panel_info(driver.page_source)
    #     driver.close()
    # # res = button.click()
    # print(res.title)
