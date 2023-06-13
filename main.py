"""
Automates the gathering of useful Fantasy Baseball Player Data.
Exclusively the ESPN Fantasy Universe from the league's Player Rater page.
v 1.6.0
modified: 07 JUN 2023
by pubins.taylor
"""
from time import sleep
import re
import os
import subprocess

import bs4

from src.DriverKit import DKDriverConfig
import src.IOKit as IOKit
from src.Globals import dirHQ
from src.PlayerKit import Player

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

rawHTML: str = ""
players: list[Player] = []


def getESPNPlyrUniverse(url: str, headless: bool = True):
    """
    Function that navigates to the league's player rater URL.
    :param url: string corresponding to the article destination.  This changes from preseason to regular season
    :param headless: boolean that determines whether to run the browser in headless mode
    :return: none
    """
    sdrvr = DKDriverConfig(dirDownload=dirHQ, headless=headless)
    sdrvr.get(url)
    sdrvr.implicitly_wait(10)

    # sort the page by %Rostered
    pctRosteredButton = sdrvr.find_element(By.XPATH, "//th[div[span[contains(text(),'%ROST')]]]")
    pctRosteredButton.click()
    # get the position radio buttons
    pickerGroup = sdrvr.find_element(By.CSS_SELECTOR, "#filterSlotIds")
    position_buttons = pickerGroup.find_elements(By.TAG_NAME, "label")
    # create empty table to hold the combined data
    # this table will combine all the pages of data into one table
    combinedTable = BeautifulSoup('', 'lxml').new_tag('table')
    for button in position_buttons:
        posGroup = button.text
        if posGroup == "Batters" or posGroup == "Pitchers":
            try:
                button.click()
                sleep(1)
                # give the page time to load
                WebDriverWait(sdrvr, 5).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, "tbody.Table__TBODY")))
                print(f"Processing {posGroup} group")
                # TODO: add logic to make sure the appended table is different than the previous one,
                #  otherwise, shed and move forward
                combinedTable.append(parsePosGroup(sdrvr, posGroup))

            except Exception as e:
                print(f"An error occurred in getESPNPlyrUniverse while processing {posGroup}. Error message: {e}")
                continue

    # add the combined table to the rawHTML list
    global rawHTML  # bring in global variable
    rawHTML = combinedTable.prettify()
    assert len(rawHTML) > 0, "rawHTML is empty, run again"
    # write out the combined table to a file
    sdrvr.close()
    IOKit.writeOut(fileName="tempESPNPlayerUniverse", ext=".html", content=rawHTML)


def parsePosGroup(sdrvr: webdriver, posGroup: str) -> bs4.Tag:
    """
    Function that parses the HTML of multiple position group pages and returns the table of player data
    :param sdrvr: webdriver object
    :param posGroup: "Batters" or "Pitchers"
    :return: a combined table of player data
    """
    combinedTable = BeautifulSoup('', 'lxml').new_tag('table')
    page = 1
    pctRostered: float = 99.9
    while pctRostered > 1.0 or page < 3:
        try:
            WebDriverWait(sdrvr, 7).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, "tbody.Table__TBODY")))
            # get the HTML of the page and parse it with BeautifulSoup
            soup = BeautifulSoup(sdrvr.page_source, 'lxml')
            # there are 2 tables on the page,
            # the first is the player names and the second is the player rater data
            tables = soup.find_all('table')[:2]

            # there are 2 header rows, shed the first one with [1:] slicing
            playerInfoColumns = tables[0].find_all('tr')[1:]
            playerRaterColumns = tables[1].find_all('tr')[1:]
            # add the same rows from each table to the combined table
            pctRostered: float
            for i in range(0, len(playerInfoColumns)):
                if i == 0 and page == 1 and posGroup == "Batters":  # only add the headers once
                    headers = playerInfoColumns[i].contents + playerRaterColumns[i].contents
                    combinedHeaderRow = BeautifulSoup('', 'lxml').new_tag('thead')
                    for header in headers:
                        combinedHeaderRow.append(header)
                    # print(combinedHeaderRow)
                    combinedTable.append(combinedHeaderRow)
                elif i > 0:
                    wholeRow = playerInfoColumns[i].contents + playerRaterColumns[i].contents
                    combinedPlayerRow = BeautifulSoup('', 'lxml').new_tag('tr')
                    for plyr in wholeRow:
                        combinedPlayerRow.append(plyr)
                    # updated the pctRostered variable
                    pctRostered = float(combinedPlayerRow.select_one("div[title*='rostered']").string)
                    combinedTable.append(combinedPlayerRow)
                else:
                    continue  # if i (row) == 0 on any other page, then skip it
            # go to the next page
            print(f"Finished processing page {page} for {posGroup}")
            page += 1
            # always to click to next page, pctRostered will be checked at the top of the loop
            sleep(1)
            next_button = WebDriverWait(sdrvr, 7).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.Button.Pagination__Button--next")))
            # scroll button into view before clicking
            # ActionChains(sdrvr).move_to_element(next_button).perform()
            next_button.click()
            sleep(1)

        except Exception as e:
            print(f"An error occurred while processing page {page}. Error message: {e}")
            continue

    if page < 4:
        print(f"Only {page - 1} pages were processed for {posGroup}. \n should check failure")

    print(f"The lowest %Rostered for {posGroup} group was {pctRostered}")
    print(f"A total of {page - 1} pages were processed for {posGroup} group. \n" +
          f"{len(combinedTable)} players added")
    assert len(combinedTable) > 0, "No players were added to the combined table"
    return combinedTable


def fetchPlayerKeyMap() -> pd.DataFrame:
    # check to see if KeyMap.json exists before proceeding
    # if it does, then read it in and return it
    # if it doesn't, call subprocess and write it out to a json file
    # then return the dataframe
    filename = "mtblKeyMap.json"
    try:
        keyMap = os.path.join(dirHQ, filename)
        df = pd.read_json(keyMap, convert_axes=False)
        # specify the columns ESPNID, IDFANGRAPHS, MLBID as strings
        df = df.astype({"ESPNID": str, "MLBID": str})
        # print(df)
        print(f"found {filename}, returning dataframe")
        return df
    except FileNotFoundError:
        # fetch the data with the MTBL_KeyMap script
        subprocess.run(["/Users/Shared/BaseballHQ/tools/MTBL_KeyMap/.venv/bin/python3",
                        "/Users/Shared/BaseballHQ/tools/MTBL_KeyMap/main.py"])
        fetchPlayerKeyMap()


def buildPlayerUniverse(dfKeyMap: pd.DataFrame):
    """
    Function that parses the ESPN Fantasy Universe HTML file and extracts the player names and their ESPN Player IDs.
    This function is dependent on the ESPN Fantasy Universe HTML file being downloaded and saved to the project root.
    :param dfKeyMap: pandas dataframe that contains the player key map
    :return: none
    """
    os.environ['PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT'] = '1.5s'
    print("Building player universe from raw HTML")
    global rawHTML  # global keyword allows access to the global variable
    if rawHTML == "":
        rawHTML = IOKit.readIn(fileName='tempESPNPlayerUniverse', ext=".html")

    soup = BeautifulSoup(rawHTML, 'lxml')
    # print(soup.prettify())
    global players

    playerRows = soup.find_all("tr")

    for player in playerRows:  # first row is designated by the "th" tag, so no need to skip it here
        playerData = player.find_all("td")
        # location ID can be in either the src or data-src attribute
        # if both are present, then data-src is the one to use
        idLoc: str = playerData[1].find("img").get("data-src") or playerData[1].find("img").get("src")
        try:
            espnID = re.findall(r'full/(\d+)\.png', idLoc)[0]
        except Exception as e:
            print(f"cannot find espnID in html for {playerData[1].get_text(strip=True)}.  Error message: {e}")
            continue
        # shohei player id is 39382
        try:
            fangraphsID = dfKeyMap[dfKeyMap["ESPNID"] == espnID]["FANGRAPHSID"].values[0]
            savantID = dfKeyMap[dfKeyMap["ESPNID"] == espnID]["MLBID"].values[0]
            players.append(Player().from_data(playerData, espnID, fangraphsID, savantID))
        except IndexError as ie:
            print(f"Error occurred while processing {playerData[1].get_text(strip=True)}: {espnID}. \n"
                  f"   No matching player found in the key map")
            pctRostered = float(playerData[16].get_text(strip=True))
            if pctRostered > 2.0:
                print(f"   player is rostered {pctRostered} of leagues, update/add player to key map!")
            continue

    print(f"Finished building player universe.  {len(players)} players found.")

    # save the player universe to a json file
    IOKit.writeOut(dir=dirHQ, fileName="espnPlayerUniverse", ext=".json", content=players)


def deleteTempFiles():
    """
    Function that deletes the temp files that were created during the execution of the program
    :return: none
    """
    # delete any file that starts with "temp"
    for file in os.listdir():
        if file.startswith("temp"):
            os.remove(file)


def main():
    leagueID = "10998"
    espnPlayerRaterURL = "https://fantasy.espn.com/baseball/playerrater?leagueId=" + leagueID

    print("\n---Running Fantasy Data Getter---\n")

    dfKeyMap = fetchPlayerKeyMap()
    # check to see if tempESPNPlayerRater.html exists; if not, download it
    if not os.path.exists("tempESPNPlayerUniverse.html"):
        getESPNPlyrUniverse(url=espnPlayerRaterURL, headless=False)

    buildPlayerUniverse(dfKeyMap=dfKeyMap)

    deleteTempFiles()

    print("\n---Finished Fantasy Data Getter---")


if __name__ == '__main__':
    main()
