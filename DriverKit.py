# DriverKit.py
# by pubins.taylor
# created 10MAY22
# v0.1
# Houses the generics for Selenium WebDriver for multiple uses

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import os
import glob
import time
import pandas as pd
from enum import Enum


class SDKit(webdriver):
    """
    SeleniumDriverKit should be instantiated by SDKit(dirDownload).driver
    """

    def __int__(self, dirDownload: str = "/Users/Shared/Baseball HQ", headless: bool = True):
        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": dir_builder(dirDownload)}
        # example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
        options.add_experimental_option("prefs", prefs)
        options.headless = headless
        # Set the load strategy so that it does not wait for adds to load
        caps = DesiredCapabilities.CHROME
        caps["pageLoadStrategy"] = "none"
        self.driver = webdriver.Chrome(options=options, desired_capabilities=caps)

    def get(self, url: str, wait: int = 5):
        self.driver.get(url)
        self.driver.implicitly_wait(wait)

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
