"""
Automates the gathering of useful Fantasy Baseball Data.  To include the ESPN Fantasy Universe, the Fangraphs
Projections, & the Baseball Savant expected stats.
v1.1
19MAY2022
by pubins.taylor
"""
import time

import DriverKit
import SaveKit
from Globals import dirHQ, FGSystem, Savant

from selenium.common import exceptions
from selenium.webdriver.common.by import By
import pandas


def getESPNPlyrUniverse(url: str):
    """
    Function that navigates to a url article that hosts Eric Karabel's (ESPN Fantasy Expert) weekly updated top 300
    Fantasy Baseball players in H2H Categories Leagues.  This list serves as the viable Fantasy Player Universe that
    sets the limits for players worth analyzing.
    :param url: string corresponding to the article destination.  This changes from preseason to regular season
    :return: none
    """
    sdrvr = DriverKit.driverConfig(dirDownload=dirHQ, headless=True)
    sdrvr.get(url)
    sdrvr.implicitly_wait(10)
    elmArticle = sdrvr.find_element(By.CSS_SELECTOR, 'div.article-body')
    rawHTML = elmArticle.get_attribute("innerHTML")
    sdrvr.close()
    SaveKit.writeOut(dir=dirHQ, fileName='h2hPlayerList', ext=".html", content=rawHTML)


def getFangraphsProjections(projSys: [FGSystem] = (FGSystem.Steamer_RoS,)):
    """
    Function that takes a requested projection system, builds URLs to match request, invokes Selenium to download the
    .csv, and renames the file according to the requested projection system
    :param projSys: Projection System is an Enum that corresponds to an available projection system; reduces to a string
    :return: none
    """
    # ATC will only be used for preseason projections and thus placed in the appropriate directory
    if projSys == FGSystem.ATC:
        dirFG = dirHQ + "preseason/"
    else:
        dirFG = dirHQ + "regseason/"
    urls: list[dict] = DriverKit.fgLinkBuilder(projSys)
    for url in urls:
        sdrvr = DriverKit.driverConfig(dirDownload=dirFG, headless=False)
        sdrvr.get(url["url"])
        try:
            # hard sleep
            time.sleep(4)
            sdrvr.execute_script("window.scrollBy(0,316)")
            # Wait a reasonable time that a person would take
            sdrvr.implicitly_wait(15)
            # Wait until the element to download is available and then stop loading
            sdrvr.find_element(By.LINK_TEXT, "Export Data").click()
            print("clicked 'Export Data'")
            time.sleep(3)
        except Exception as e:
            print(e.message)
        sdrvr.close()
        # Every file downloaded from FanGraphs is labeled "FanGraphs Leaderboard.csv"
        downloadedFile = "FanGraphs Leaderboard.csv"
        # Fangraphs csvs have column separators that produce NA data columns with duplicative headers; those need to be
        # removed or will not be ingestible
        df = pandas.read_csv(dirFG + downloadedFile)
        # print(df)
        df.dropna(axis=1, how="all", inplace=True)
        # print(df)
        df.to_csv(dirFG + downloadedFile, index=False)
        SaveKit.renameFile(dir=dirFG, fExt=".csv", downloadedFile=downloadedFile, newFileName=url["id"])


def getSavantData(statcastData: [Savant]):
    """
    Receives requested baseball savant data products, builds URLs to match request, invokes Selenium to download the
    .csv, and renames the file according to the dataset
    :param statcastData: Savant enum representing the desired statcast data object
    :return: none
    """

    dirSvnt = dirHQ + "regseason/"
    savantDestinations: list[dict] = DriverKit.savantLinkBuilder(statcast=statcastData)
    for dest in savantDestinations:
        sdrvr = DriverKit.driverConfig(dirDownload=dirSvnt, headless=True)
        sdrvr.get(dest["url"])
        try:
            # Wait a reasonable time that a person would take
            sdrvr.implicitly_wait(15)
            # Wait until the element to download is available and then stop loading
            downloadBtn = sdrvr.find_element(By.ID, "btnCSV")
            time.sleep(3)
            downloadBtn.click()
            print("clicked 'Download CSV'")
            time.sleep(3)
        except exceptions as e:
            sdrvr.close()
            print(e.message)
        sdrvr.close()

        SaveKit.renameFile(dir=dirSvnt, fExt=".csv", downloadedFile=dest["download"], newFileName=dest["id"])


if __name__ == '__main__':
    getESPNPlyrUniverse(url="https://www.espn.com/fantasy/baseball/story/_/id/33208450/fantasy-baseball-rankings-head"
                            "-head-category-rotiserrie-leagues-2022")
    getFangraphsProjections(projSys=[FGSystem.Steamer_RoS])
    getSavantData(statcastData=[Savant.xStats])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
