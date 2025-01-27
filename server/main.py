import traceback
from uuid import uuid4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from sys import argv
import time
import json
import os
import tempfile
from functools import reduce
import pickle
import logging as logger

from selenium.webdriver.support.expected_conditions import presence_of_element_located, element_to_be_clickable
from selenium.webdriver.support.wait import WebDriverWait
#from undetected_chromedriver import Chrome

logger.basicConfig(level = logger.INFO,format='%(asctime)s - %(levelname)s - %(message)s')


def save_cookies(driver):
    driver.get("http://meet.google.com")
    input("Press Enter after you logged in...")
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    logger.info("Saved Cookies!")


def create_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--use-fake-ui-for-media-stream")
#    options.add_argument("--use-fake-device-for-media-stream")
#    options.add_argument(r'--use-file-for-fake-video-capture=./720.y4m')

    options.add_argument('--headless')  # Ensure headless mode is active
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')  # Mitigate resource limits on VPS
#    options.add_argument('--window-size=1920,1080')  # Set browser resolution
    options.add_argument('--disable-gpu')  # Mitigate resource limits on VPS

#    options.add_argument('--window-size=2560,1440')
#    options.add_argument('window-size=2560,1440')
    # prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
    # options.add_experimental_option("prefs", prefs)
    # options.add_experimental_option('prefs', {'download.default_directory':'./Downloads'})
#    service = Service("/usr/bin/chromedriver")
#    driver = webdriver.Chrome(service=service, options=options)

    options.set_preference("media.navigator.permission.disabled", True)
    service = Service("./geckodriver")
    driver = webdriver.Firefox(service=service, options=options)
    # driver = Chrome(options = options)
    return driver


def start_sharing(driver:WebDriver, meet_url, cookies):
    driver.get(meet_url)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

    try:
#        driver.save_screenshot(uuid4().hex + '.png')
        join_button = WebDriverWait(driver, 10).until(element_to_be_clickable((By.XPATH, "//button[span[text()='Join now'] or span[text()='Switch here']]")))
        join_button.click()
        logger.info("Joining to the Meet...")
        WebDriverWait(driver, 10).until(presence_of_element_located((By.XPATH, "//div[contains(text(), 'Turn off camera')]")))
        logger.info("Started streaming...")

        button = WebDriverWait(driver, 2).until(presence_of_element_located((By.XPATH, "//button[@aria-label='More options' and not (contains(@jsaction, 'mouseup'))]")))
        driver.execute_script("arguments[0].click();", button)
        settings = WebDriverWait(driver, 2).until(presence_of_element_located((By.XPATH, "//span[text()='Settings']")))
        driver.execute_script("arguments[0].click();", settings)
        general_settings = WebDriverWait(driver, 2).until(presence_of_element_located((By.XPATH, "//button[@aria-label='General']")))
        driver.execute_script("arguments[0].click();", general_settings)
        disable_leave_call = WebDriverWait(driver, 2).until(presence_of_element_located((By.XPATH, "//button[@aria-label='Leave empty calls']")))
        driver.execute_script("arguments[0].click();", disable_leave_call)
        close = WebDriverWait(driver, 2).until(presence_of_element_located((By.XPATH, "//button[@aria-label='Close dialog']")))
        driver.execute_script("arguments[0].click();", close)

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Could not join the Meet:", str(e))
    
    while(True):
        driver.save_screenshot(uuid4().hex + '.png')
        time.sleep(60)


    input("Press Enter to close...")
    driver.quit()

if __name__ == "__main__":
    if '--export-cookies' in argv:
        driver = create_driver()
        save_cookies(driver)
    elif "--url" in argv:
        driver = create_driver()
        cookies_file = argv[argv.index("--cookies") + 1]
        meet_url = argv[argv.index("--url") + 1]
        cookies = pickle.load(open(cookies_file, "rb"))
        start_sharing(driver, meet_url, cookies)

    else:
        text = (
            "Specify one of the options:\n\n"
            "--url url --cookies cookies\n\n"
            "--export-cookies"
        )
        logger.error(text)
