import json
from bs4 import BeautifulSoup
import chompjs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# with open("Inghilterra-Premier-League-Tottenham-Manchester-City", "r") as f:
#     html_content = f.read()
url = "https://it.whoscored.com/Matches/1746314/Live/Italia-Serie-A-Atalanta-Fiorentina"
# url = "https://it.whoscored.com/Matches/1729441/Live/Inghilterra-Premier-League-2023-2024-Tottenham-Manchester-City"
driver = webdriver.Chrome()

# Open the web page
driver.get(url)
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="#chalkboard"]')))#.click()
print(driver.page_source)
# element = driver.find_element(By.CSS_SELECTOR, 'a[href="#chalkboard"]')#.find_element(By.CSS_SELECTOR, "span")
# print(element)
# res = element.click()
# print(res)