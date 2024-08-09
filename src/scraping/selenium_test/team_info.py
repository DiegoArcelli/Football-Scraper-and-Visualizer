import json
import chompjs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

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

# # Isolate the JSON part from the script content
json_str = html_content.split('require.config.params["args"] =')[1].rsplit(';', 1)[0]
# print(json_str)
# # Parse the JSON string into a Python dictionary
data  = chompjs.parse_js_object(json_str)
match_centre = data["matchCentreData"]
print(match_centre.keys())
# print(match_centre["periodMinuteLimits"])
# print(match_centre["minuteExpanded"])
# print(match_centre["maxPeriod"])
print(match_centre["periodEndMinutes"])
# print(match_centre["playerIdNameDictionary"])

# print(data["formationIdNameMappings"])
# event_types = data["matchCentreEventTypeJson"]
# players_mapping = data["matchCentreData"]["playerIdNameDictionary"]

# for event_type in event_types:
#     print(event_type + ":", data["matchCentreEventTypeJson"][event_type])
