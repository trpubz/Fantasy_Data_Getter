import glob
import os
import time

import selenium.webdriver.chromium.webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import DriverKit
import SaveKit
from Globals import *


def getESPNPlyrUniverse(url: str):
    sdrvr = DriverKit.driverConfig(dirDownload=dirHQ, headless=False)
    sdrvr.get(url)
    sdrvr.implicitly_wait(10)
    elmArticle = sdrvr.find_element(By.CSS_SELECTOR, 'div.article-body')
    rawHTML = elmArticle.get_attribute("innerHTML")
    sdrvr.close()
    SaveKit.writeOut(dir=dirHQ, fileName='h2hPlayerList', ext=".html", content=rawHTML)


def getFangraphsProjections(projSys=Projections.Steamer_RoS):
    # ATC will only be used for preseason projections and thus placed in the appropriate directory
    if projSys == Projections.ATC:
        dirFG = dirHQ + "preseason/"
    else:
        dirFG = dirHQ + "regseason/"
    urls: list[dict] = DriverKit.fgLinkBuilder(projSys)
    for url in urls:
        sdrvr = DriverKit.driverConfig(dirDownload=dirFG, headless=False)
        sdrvr.get(url["fgURL"])
        try:
            # hard sleep
            time.sleep(2)
            # Wait a reasonable time that a person would take
            sdrvr.implicitly_wait(15)
            # Wait until the element to download is available and then stop loading
            sdrvr.find_element(By.LINK_TEXT, "Export Data").click()
            time.sleep(2)
        except exceptions as e:
            print(e.message)
        sdrvr.close()

        # get all the .csv files in the download directory
        files = glob.glob(dirFG + "/*.csv")
        for f in files:
            # the file will always download as 'FanGraphs Leaderboard.csv'
            if f.__contains__("FanGraphs"):
                newFileName = url["id"]  # part of the URL object group
                # remove old files
                for removable in files:
                    if removable.__contains__(newFileName):
                        os.remove(removable)
                newDownloadPath = dirFG + newFileName + ".csv"
                os.rename(f, newDownloadPath)
                # locCSVs.append(newDownloadPath)
                print(f"successfully downloaded {newFileName} to {dirFG}")
                break


def getSavantData():
    pass


if __name__ == '__main__':
    getESPNPlyrUniverse(url="https://www.espn.com/fantasy/baseball/story/_/id/33208450/fantasy-baseball-rankings-head"
                            "-head-category-rotiserrie-leagues-2022")
    getFangraphsProjections(projSys=Projections.Steamer_RoS)
    getSavantData()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
