""" A script aimed to send messages via messenger"""


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains as A
from selenium.webdriver.common.keys import Keys as K
from selenium.webdriver.support.ui import Select
import os
import time
import config

# suppression des affichages de webdriver-manager
os.environ["WDM_LOG_LEVEL"] = "0"
os.environ["WDM_PRINT_FIRST_LINE"] = "False"


def connect():
    """Set up of the bot"""

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    browser = webdriver.Chrome(
        ChromeDriverManager().install(), options=options
    )  # maybe shoud i've call it driver
    browser.get("https://www.messenger.com/t/100010820648031")
    accept = browser.find_elements_by_class_name("_42ft")
    accept[3].click()

    inputs = browser.find_elements_by_class_name("inputtext")
    inputs[0].send_keys(config.USR)
    inputs[1].send_keys(config.PWD)
    inputs[1].send_keys(K.ENTER)

    time.sleep(2)
    return browser


def send_message(browser, message):
    """Send the message in message string"""
    action = A(browser)
    action.send_keys(message + "\n").perform()


if __name__ == "__main__":
    browser = connect()
    send_message(browser, "Hello world")
