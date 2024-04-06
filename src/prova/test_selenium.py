from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def parse_gk_table(table, team_name):

    players_stats = {}
    team_stats = {}

    table_header = table.select('thead')[0]
    table_body = table.select('tbody')[0]

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


    gk_num = len(players_stats.values[0])

    if gk_num > 1:

        for attribute in ["gk_shots_on_target_against", "gk_goals_against", "gk_saves", "gk_psxg", "gk_passes_completed_launched", "gk_passes_launched", "gk_passes", "gk_passes", "gk_goal_kicks", "gk_crosses", "gk_crosses_stopped", "gk_def_actions_outside_pen_area"]:
            team_stats[attribute] = sum(players_stats[attribute])

        if team_stats["gk_saves"] > 0:
            team_stats["gk_save_pct"] = team_stats["gk_goals_against"]/team_stats["gk_saves"]*100

        if team_stats["gk_passes_launched"] > 0:
            team_stats["gk_passes_pct_launched"] =  team_stats["gk_passes_completed_launched"]/team_stats["gk_passes_launched"]*100

        if team_stats["gk_crosses"]:
            team_stats["gk_crosses_stopped_pct"] = team_stats["gk_crosses_stopped"]/team_stats["gk_crosses"]*100

        team_stats["gk_pct_passes_launched"] = sum([players_stats["gk_pct_passes_launched"][i]*players_stats["gk_passes"][i] for i in range(gk_num)])/sum([players_stats["gk_passes"][i] for i in range(gk_num)])
    else:
        team_stats = players_stats

    return players_stats, team_stats


def parse_table(table, team_name):

    players_stats = {}
    team_stats = {}

    table_header = table.select('thead')[0]
    table_body = table.select('tbody')[0]
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

    return players_stats, team_stats



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://fbref.com/it/partite/8b6e8a62/Udinese-Juventus-20-Agosto-2023-Serie-A")
html_content = driver.page_source
driver.close()


soup = BeautifulSoup(html_content, 'html.parser')

table_names = ["summary", "passing", "passing_types", "defense", "possession", "misc"]

for table_name in table_names:
    tables = soup.select(f'table[id^="stats_"][id$="_{table_name}"]')
    players_home, team = parse_table(tables[0], "Juve")
    players_away, team = parse_table(tables[1], "Juve")
    keys = players_home.keys()
    print(keys)


tables = soup.select(f'table[id^="keeper_stats_"]')
players_home, team = parse_table(tables[0], "Juve")
players_away, team = parse_table(tables[1], "Juve")





# # print(html_content)
# tables = soup.select('table[id^="stats_"][id$="_passing"]')
# print(len(tables))
# print(player)
# print(team)



# match_table = soup.select('table[id^="matchlogs"]')[0]
# matches = match_table.select('tr')
# print(matches)