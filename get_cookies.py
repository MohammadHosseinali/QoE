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
import undetected_chromedriver

logger.basicConfig(level = logger.INFO,format='%(asctime)s - %(levelname)s - %(message)s')


def save_cookies(driver):
    driver.get("http://meet.google.com")
    input("Press Enter after you logged in...")
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
    logger.info("Saved Cookies!")


def create_driver():
    options = webdriver.ChromeOptions()
    driver = undetected_chromedriver.Chrome(options = options)

    return driver



if __name__ == "__main__":
    driver = create_driver()
    save_cookies(driver)
