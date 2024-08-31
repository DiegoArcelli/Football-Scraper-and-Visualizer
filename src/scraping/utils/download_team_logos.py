import json
import chompjs
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
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
from .utils import *
import shutil
import requests
import os


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
    # print(league_region, league)
    for region_dict in data:
        region = region_dict["name"]
        if league_region == region:
            tournaments = region_dict["tournaments"]
            for tournament in tournaments:
                if tournament["name"] == league:
                    url = tournament["url"]

    url = "https://www.whoscored.com" + url
    return url, league


def get_league_team_logos(
        data_dir,
        logos_dir,
        league_name,
        season,
        team=None
    ):


    data_dir = f"{data_dir}{season}/"
    create_dir(data_dir)
    data_dir = f"{data_dir}{league_name}/"
    create_dir(data_dir)

    create_dir(logos_dir)
    league_dir = f"{logos_dir}{league_name}/"
    create_dir(league_dir)

    f = open("selenium_test/regions.json") 
    data = json.load(f)
    
    url, league = get_url(data, league_name)
    print(url)

    # print(url)
    # return
    # url = "https://www.whoscored.com/Regions/108/Tournaments/5/Seasons/9659/Stages/22143/Fixtures/Italy-Serie-A-2023-2024"
    # url = "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A"
    driver = webdriver.Chrome()
    driver.get(url)


    driver.find_element(By.XPATH, "//button[contains(@class, 'css-1wc0q5e')]").click()
    print("Accepted cookies")

    # button = driver.find_element(By.CSS_SELECTOR, "button[class='webpush-swal2-close']")
    try:
        driver.find_element(By.CSS_SELECTOR, "button[class='webpush-swal2-close']").click()
        print("Closed subscription banner")
    except NoSuchElementException:
        print("Subscription banner not present")

    teams_name_path = f"{data_dir}whoscored_names.txt"
    name_mapping_path = f"{data_dir}names_mapping.json"
    if not os.path.exists(teams_name_path):
        print(f"Missing {name_mapping_path}\n")
        exit()
    f = open(name_mapping_path) 
    names_map = json.load(f)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    teams_table = soup.select("table[id^='standings-']")[0]
    rows = teams_table.select("a[class='team-link']")

    for row in rows:
        team_url = row.get("href")
        team_name = row.text
        team_name = names_map[team_name]


        team_path = f"{league_dir}{team_name}.png"
        print(f"\n{team_name}")

        if os.path.exists(team_path):
            print(f"Logo already saved in {team_path}")
            continue

        team_url = f"https://www.whoscored.com{team_url}"
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(team_url)

        team_soup = BeautifulSoup(driver.page_source, 'html.parser')
        logo = team_soup.select("img[class='team-emblem']")[0]
        logo_url = logo.get("src")
        print(logo_url)
        print(f"Logo dowloaded in {team_path}")

        

        r = requests.get(logo_url, stream=True)
        if r.status_code == 200:
            with open(team_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)        
            
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.close()