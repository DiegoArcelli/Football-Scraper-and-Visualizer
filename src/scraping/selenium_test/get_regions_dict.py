import json
import chompjs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException



# with open("Inghilterra-Premier-League-Tottenham-Manchester-City", "r") as f:
#     html_content = f.read()
# url = "https://it.whoscored.com/Matches/1746314/Live/Italia-Serie-A-Atalanta-Fiorentina"
# url = "https://it.whoscored.com/Matches/1729441/Live/Inghilterra-Premier-League-2023-2024-Tottenham-Manchester-City"
url = "https://www.whoscored.com/Matches/1809759/Live/Europe-Champions-League-Manchester-City-Real-Madrid"

driver = webdriver.Chrome()

# Open the web page
driver.get(url)

try:
    driver.find_element(By.XPATH, "//button[contains(@class, 'css-1wc0q5e')]").click()
    print("Accepted cookies")
except NoSuchElementException:
    pass

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

# select("//select[contains(@id, 'locale-select')]", "EN")

html_content = driver.page_source


json_str = html_content.split("var allRegions = ")[1].split(";")[0]
regions  = chompjs.parse_js_object(json_str)
for region in regions:
    print(region)


import json 

# Convert and write JSON object to file
with open("regions.json", "w") as outfile: 
    json.dump(regions, outfile)