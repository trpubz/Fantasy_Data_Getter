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
from Globals import Projections, StatGrp


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

@staticmethod
def url_builder(projections: [Projections], pos: [StatGrp] = [StatGrp.HIT, StatGrp.PIT]) -> [{str: str}]:
    """
    :param projections: A list of Projections enums representing the desired FanGraphs projection options
    :param pos: A list of position groups. Either hitters, pitchers, or both.  Defaults to both
    :return: A list of dictionary items.  The list represents the URL objects and the dict is keyed by the URL id which
    is used to save the file with the proper naming convention and keyed by the fgURL which is the URL link.
    Builds URLs based on user need.
    """
    urls = []
    for grp in pos:
        for proj in projections:
            fgURL = "https://www.fangraphs.com/projections.aspx?pos=all&stats=" + grp.value + "&type=" + \
                    proj.value + "&team=0&lg=all&players=0"
            fg = {"id": proj.value + "_" + grp.value, "fgURL": fgURL}
            urls.append(fg)

    return urls