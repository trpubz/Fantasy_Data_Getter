# DriverKit.py
# by pubins.taylor
# created 10MAY22
# v0.1
# Houses the generics for Selenium WebDriver for multiple uses
import os

from Globals import FGSystem, FGPosGrp, Savant, SavantPosGrp, SavantDownload

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def DKDriverConfig(dirDownload: os.path = "root", headless=True) -> webdriver:
    """
    Handles redundant webdriver config management by passing the desired options as arguments.
    :param dirDownload: type os.path (string).  The driver will download files, like a .csv, to this directory.
    :param headless: boolean.  Indicates whether to draw the webdriver window.
    :return: selenium.webdriver
    """
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": dirDownload}
    # example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
    options.add_experimental_option("prefs", prefs)
    if headless==True:
        options.add_argument("--headless")
    # Set the load strategy so that it does not wait for adds to load
    caps = DesiredCapabilities.CHROME
    caps["pageLoadStrategy"] = "none"
    # ChromeDriverManager().install() downloads latest version of chrome driver to avoid compatibility issues
    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()), desired_capabilities=caps)

    return driver


def DKDirBuilder(dirDownload: str = "root") -> os.path:
    """
    Builds a directory on the user preference.
    :param dirDownload: String representation of the desired directory to download.  If nothing passed,
    defaults to the project's root directory.
    :return: the os.path which is a string
    """

    outputPath: os.path

    if dirDownload == "root":
        projectRoot = os.path.dirname(__file__)
        outputPath = projectRoot + '/csvs'
    elif dirDownload.startswith('C:\\') or dirDownload.startswith('/Users'):
        outputPath = dirDownload
    else:
        raise NotADirectoryError()

    return outputPath


def DKFGLinkBuilder(*projections: list[FGSystem], pos: list[FGPosGrp] = (FGPosGrp.HIT, FGPosGrp.PIT)) -> list[dict[str, str]]:
    """
    Builds Fangraphs URLs based on user need.
    :param projections: A list of Projections enums representing the desired FanGraphs projection options
    :param pos: A list of position groups. Either hitters, pitchers, or both.  Defaults to both
    :return: A list of dictionary items.  The list represents the URL objects and the dict is keyed by the URL id which
    """

    urls = []
    for grp in pos:
        for proj in projections:
            fgURL = "https://www.fangraphs.com/projections.aspx?pos=all&stats=" + grp.value + "&type=" + \
                    proj.value + "&team=0&lg=all&players=0"
            fg = {"id": proj.value + "_" + grp.value, "url": fgURL}
            urls.append(fg)

    return urls


def DKSavantLinkBuilder(statcast: list[Savant], pos: list[SavantPosGrp] = (SavantPosGrp.HIT, SavantPosGrp.PIT)) -> list[dict[str: str]]:
    """
    Builds baseball.savant URLs based on user need.
    :param statcast: A list of Savant enums representing the desired baseball savant stats
    :param pos: A list of position groups. Either hitters, pitchers, or both.  Defaults to both
    :return: A list of dictionary items.  The list represents the URL objects and the dict is keyed by the URL id which
    """

    minEvents: str
    urls = []
    for grp in pos:
        if grp == SavantPosGrp.HIT:
            minEvents = "25"  # stands for qualified
        elif grp == SavantPosGrp.PIT:
            minEvents = "1"
        for stats in statcast:
            url = "https://baseballsavant.mlb.com/leaderboard/" + stats.value + "?type=" + grp.value + "&min=" \
                      + minEvents
            if stats == Savant.xStats:
                download = SavantDownload.xStats
            savant = {
                "id": stats.value + "_" + grp.value[0:3],  # subscript operator to get the first 3 letters
                "url": url,
                "download": download.value
            }
            urls.append(savant)

    return urls


def DKCheckDownloadsChrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        """)