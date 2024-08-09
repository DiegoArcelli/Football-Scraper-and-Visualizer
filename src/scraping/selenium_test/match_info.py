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
# url = "https://it.whoscored.com/Matches/1729441/Live/Inghilterra-Premier-League-2023-2024-Tottenham-Manchester-City"
url = "https://www.whoscored.com/Matches/1812181/Live/International-European-Championship-Turkiye-Georgia"
url = "https://www.whoscored.com/Matches/1809759/Live/Europe-Champions-League-Manchester-City-Real-Madrid"
driver = webdriver.Chrome()

# Open the web page
driver.get(url)
html_content = driver.page_source

# # Isolate the JSON part from the script content
json_str = html_content.split("require.config.params['matchheader'] = ")[1].split(";")[0].replace("\n", " ")
json_list = json_str.split("[")[1].split("]")[0].split(",")
match_id = json_str.replace(" ", "").split("matchId:")[1].split("}")[0]
print(match_id)

match_info = {}

input_list = []
for element in json_list:
    val = element
    if element == "":
        val = None
    elif element[0] == "'" and element[-1] == "'":
        val = element[1:-1]
    input_list.append(val)

match_info["input"] = input_list
match_info["match_id"] = match_id
print(match_info)



# print(json_str)
# # Parse the JSON string into a Python dictionary
# json_str = "{input: [30,167,'Tottenham','Manchester City','14/05/2024 21:00:00','14/05/2024 00:00:00',6,'FIN','0 : 0','0 : 2', , ,'0 : 2','Inghilterra','Inghilterra'], matchId: 1729441 }"
# data  = chompjs.parse_js_object(json_str)
# print(data)