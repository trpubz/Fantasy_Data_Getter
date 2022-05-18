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
    sdrvr = DriverKit.driver_config(dirDownload=dirHQ, headless=False)
    sdrvr.get(url)
    sdrvr.implicitly_wait(10)
    elmArticle = sdrvr.find_element(By.CSS_SELECTOR, 'div.article-body')
    rawHTML = elmArticle.get_attribute("innerHTML")
    sdrvr.close()
    SaveKit.write_out(dir=dirHQ, fileName='h2hPlayerList', ext=".html", content=rawHTML)


def getFangraphsProjections(projSys="steamerr"):
    dirFG = dirHQ + "regseason/"
    urls: list[dict] = DriverKit.url_builder(projSys)
    for url in urls:
        sdrvr = DriverKit.driver_config(dirDownload=dirFG, headless=False)
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
                print(fr"successfully downloaded {newFileName} to {dirFG}")
                sdrvr.close()
                break


def getSavantData():
    pass


if __name__ == '__main__':
    getESPNPlyrUniverse(url="https://www.espn.com/fantasy/baseball/story/_/id/33208450/fantasy-baseball-rankings-head"
                            "-head-category-rotiserrie-leagues-2022")
    getFangraphsProjections(projSys=Projections.Steamer_RoS)
    getSavantData()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
