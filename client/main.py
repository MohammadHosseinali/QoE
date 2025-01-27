import traceback
from datetime import datetime
from uuid import uuid4

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from sys import argv
import time
import json
import pickle
import logging as logger
from time import sleep
from selenium.webdriver.support.expected_conditions import presence_of_element_located, element_to_be_clickable
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
import signal_info
from itu_p1203 import extractor
from itu_p1203 import p1203_standalone
import os
import db
from pprint import pprint


logger.basicConfig(level = logger.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloads")
database = db.Database('db.sqlite')

def save_cookies(driver):
    driver.get("http://meet.google.com")
    input("Press Enter after you logged in...")
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    logger.info("Saved Cookies!")


def create_driver():
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")

    # prefs = {"profile.default_content_setting_values.automatic_downloads": 1,
    #         "profile.default_content_settings.popups": 0,
    #          "download.default_directory": r"Downloads",  ### Set the path accordingly
    #          "download.prompt_for_download": False,  ## change the downpath accordingly
    #          "download.directory_upgrade": True
    #          }
    print(download_path)
    prefs = {"download.default_directory": download_path}
    options.add_experimental_option("prefs", prefs)

    # run Chrome in headless mode
    # options.headless = True

    # set up the WebDriver for Chrome
    # driver = uc.Chrome(
    #     options=options,
    # )
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def set_cookies(driver, meet_url, cookies):
    logger.info(meet_url)
    driver.get(meet_url)
    for cookie in cookies:
        driver.add_cookie(cookie)


def join_meet(driver:WebDriver, meet_url):
    try:
        driver.get(meet_url)
        join_button = WebDriverWait(driver, 10).until(element_to_be_clickable((By.XPATH, "//button[span[text()='Join now'] or span[text()='Switch here']]")))
        join_button.click()
        logger.info("Joined the Meet")
        logger.info("Waiting 20 seconds before starting the test")
        sleep(10)
        try:
            signal = signal_info.get_signal_info('http://192.168.8.1/')
            logger.info(signal)
            rssi = signal.get('rssi')
            sinr = signal.get('sinr')
            rsrq = signal.get('rsrq')
            rsrp = signal.get('rsrp')
            driver.execute_script(open('../QoE.js', 'r').read())
            logger.info("Downloading Video..")
            sleep(10)
            filename = max([f for f in os.listdir(download_path)],
                        key=lambda xa: os.path.getctime(os.path.join(download_path, xa)))
            full_path = os.path.join(download_path, filename)
            logger.info(full_path)
        except:
            logger.error(traceback.format_exc())
        # Calculate MOS
        try:
            video = extractor.Extractor([full_path], mode = 0)
            result = p1203_standalone.P1203Standalone(video.extract()).calculate_complete()
            pprint(type(result))
            pprint(result)
            MOS = result.get('O46')
        except:
            logger.error(traceback.format_exc())

        try:
            database.add_record(rssi, sinr, rsrq, rsrp, MOS, datetime.now())
            logger.info("Saved results")
        except:
            logger.error(traceback.format_exc())



        # logger.info("Started streaming")
    except Exception as e:
        logger.error("An Error occured:", str(e))
        logger.error(traceback.format_exc())
    # driver.quit()

if __name__ == "__main__":
    if '--export-cookies' in argv:
        driver = create_driver()
        save_cookies(driver)
    elif "--url" in argv:
        driver = create_driver()
        cookies_file = argv[argv.index("--cookies") + 1]
        meet_url = argv[argv.index("--url") + 1]
        cookies = pickle.load(open(cookies_file, "rb"))
        set_cookies(driver, meet_url, cookies)
        while True:
            join_meet(driver, meet_url)

    else:
        text = (
            "Specify one of the options:\n\n"
            "--url url --cookies cookies\n\n"
            "--export-cookies"
        )
        logger.error(text)
