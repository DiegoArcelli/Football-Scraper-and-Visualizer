import json
import chompjs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def assign(data, key):
    try:
        return data[key]
    except KeyError:
        return None


# with open("Inghilterra-Premier-League-Tottenham-Manchester-City", "r") as f:
#     html_content = f.read()
url = "https://it.whoscored.com/Matches/1746314/Live/Italia-Serie-A-Atalanta-Fiorentina"
url = "https://it.whoscored.com/Matches/1729441/Live/Inghilterra-Premier-League-2023-2024-Tottenham-Manchester-City"
url = "https://www.whoscored.com/Matches/1809759/Live/Europe-Champions-League-Manchester-City-Real-Madrid"

driver = webdriver.Chrome()

# Open the web page
driver.get(url)
html_content = driver.page_source



info = html_content.split("require.config.params['matchheader'] = ")[1].split(";")[0].replace("\n", " ")
info_list = info.split("[")[1].split("]")[0].split(",")
match_id = info.replace(" ", "").split("matchId:")[1].split("}")[0]
print(match_id)

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
print(data.keys())
print(data["matchCentreData"].keys())
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
print(players_mapping)
for idx, event in enumerate(events):
    print(f"Event {idx}")
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
match_df = pd.DataFrame.from_dict(dict_df)
print(match_df.head(10))
# for key in all_keys:
#     print(key)
# # Print the parsed data
# print(data)
