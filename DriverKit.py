# DriverKit.py
# by pubins.taylor
# created 10MAY22
# v0.1
# Houses the generics for Selenium WebDriver for multiple uses

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import os
from enum import Enum


@staticmethod
def driver_config(dirDownload: os.path, headless=True) -> webdriver:
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": dirDownload}
    # example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
    options.add_experimental_option("prefs", prefs)
    options.headless = headless
    # Set the load strategy so that it does not wait for adds to load
    caps = DesiredCapabilities.CHROME
    caps["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    return driver


@staticmethod
def dir_builder(dirDownload: str = "root") -> os.path:
    """
    :param dirDownload: String representation of the desired directory to
    download.  If nothing passed, defaults to the project's root directory.

    :return: the os.path which is a string

    Builds a directory on the user preference.

    The function also removes any previously downloaded files found in the same directory with the same naming
    convention.
    """
    outputPath: os.path

    if dirDownload == "root":
        projectRoot = os.path.dirname(__file__)
        # files = glob.glob(projectRoot + "/csvs/*.csv")
        # for f in files:
        #     if f.__contains__("FanGraphs"):
        #         os.remove(f)
        outputPath = projectRoot + '/csvs'
    elif dirDownload.startswith('C:\\') or dirDownload.startswith('/Users'):
        outputPath = dirDownload
    else:
        raise NotADirectoryError()

    return outputPath


class Projections(Enum):
    # important to note Steamer_RoS is the only RoS projections with QS numbers
    DC_RoS = "rfangraphsdc"
    Steamer_RoS = "steamerr"
    ZiPS_RoS = "rzips"
    ATC = "atc"


class StatGrp(Enum):
    HIT = 'bat'
    PIT = 'pit'