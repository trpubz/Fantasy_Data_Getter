"""
Automates the gathering of useful Fantasy Baseball Player Player Data.  To include the ESPN Fantasy Universe, the Fangraphs
Projections, & the Baseball Savant expected stats.
v1.2
modified: 19 MAY 2023
by pubins.taylor
"""
from time import sleep
import re
import os
import json

from src.DriverKit import DKDriverConfig, DKDirBuilder, DKFGLinkBuilder, DKSavantLinkBuilder
import src.IOKit as IOKit
from src.Globals import dirHQ, FGSystem, Savant
from src.PlayerKit import Player

from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import lxml

rawHTML: list[str] = []
players: list[Player] = []

def getESPNPlyrUniverse(url: str):
    """
    Function that navigates to the league's player rater URL.
    :param url: string corresponding to the article destination.  This changes from preseason to regular season
    :return: none
    """
    sdrvr = DKDriverConfig(dirDownload=dirHQ, headless=True)
    sdrvr.get(url)
    sdrvr.implicitly_wait(10)
    
    global rawHTML # bring in global variable

    # get the position radio buttons
    pickerGroup = sdrvr.find_element(By.CSS_SELECTOR, "#filterSlotIds")
    position_buttons = pickerGroup.find_elements(By.TAG_NAME, "label")

    for button in position_buttons:
        posGroup = button.text
        if posGroup == "Batters" or posGroup == "Pitchers":
            try: 
                button.click()
                # give the page time to load
                sleep(5)

                # adjust number of pages depending on position
                num_pages = 11 if posGroup == "Batters" else 14
                # create empty table to hold the combined data
                # this table will combine all the pages of data into one table
                combinedTable = BeautifulSoup('', 'lxml').new_tag('table')
                for page in range(1, num_pages + 1):
                    sleep(5)
                    # get the HTML of the page and parse it with BeautifulSoup
                    soup = BeautifulSoup(sdrvr.page_source, 'lxml')
                    # find the tables
                    tables = soup.find_all('table')[:2] # there are 2 tables on the page, the first is the player names and the second is the player rater data
                    # print(tables)
                    
                    playerInfoColumns = tables[0].find_all('tr')[1:]
                    playerRaterColumns = tables[1].find_all('tr')[1:]
                    # add the same rows from each table to the combined table
                    for i in range(0, len(playerInfoColumns)):
                        if i == 0:
                            if page > 1: continue # skip the first row on all pages after the first page
                            headers = playerInfoColumns[i].contents + playerRaterColumns[i].contents
                            combinedHeaderRow = BeautifulSoup('', 'lxml').new_tag('thead')
                            for header in headers:
                                combinedHeaderRow.append(header)
                            # print(combinedHeaderRow)
                            combinedTable.append(combinedHeaderRow)
                        else:
                            wholeRow = playerInfoColumns[i].contents + playerRaterColumns[i].contents
                            combinedPlayerRow = BeautifulSoup('', 'lxml').new_tag('tr')
                            for plyr in wholeRow:
                                combinedPlayerRow.append(plyr)
                            # print(wholeRow)
                            combinedTable.append(combinedPlayerRow)
                    # go to the next page
                    print(f"Finished processing page {page} of {num_pages} for {posGroup}")
                    next_button = sdrvr.find_element(By.CSS_SELECTOR, "button.Button.Pagination__Button--next")
                    next_button.click()
                
                # add the combined table to the rawHTML list
                rawHTML.append(combinedTable.prettify())

                # write out the combined table to a file
                IOKit.writeOut(fileName="tempESPN" + posGroup, ext=".html", content=str(combinedTable.prettify()))

            except Exception as e:
                print(f"An error occurred while processing page {page}. Error message: {e}")
                continue

    sdrvr.close()

def fetchPlayerKeyMap(url) -> pd.DataFrame:
    # check to see if tempPlayerKeyMap.json exists before proceeding
    # if it does, then read it in and return it
    # if it doesn't, then fetch the data and write it out to a json file
    # then return the dataframe
    filename = "tempPlayerKeyMap.json"
    if os.path.isfile(filename):
        # If it exists, read it in and return it
        # with open(filename, 'r') as f:
        #     data = json.load(f)
        df = pd.read_json(filename, convert_axes=False)
        # specify the columns ESPNID, IDFANGRAPHS, MLBID as strings
        df = df.astype({"ESPNID": str, "MLBID": str})
        print(df)
        print(f"{filename} exists, returning dataframe")
        return df
    else:
        df = pd.read_html(url, header=1)[0] # returns a list of dataframes, so we need to index the first one, header is set to the second row
        df.dropna(subset=["MLBID", "ESPNID"], inplace=True) # drop all rows that have NaN in the ESPNID column
        df = df.astype({"ESPNID": int, "MLBID": int}) # casting from float to str requires int as an intermediate step
        df = df.astype({"ESPNID": str, "MLBID": str})
        df.to_json(filename, orient="records")
        print(df)
        print("File pulled from the interwebs, returning dataframe")
        return df

def buildPlayerUniverse(df: pd.DataFrame):
    """
    Function that parses the ESPN Fantasy Universe HTML file and extracts the player names and their ESPN Player IDs.
    This function is dependent on the ESPN Fantasy Universe HTML file being downloaded and saved to the project root.
    :param df: pandas dataframe that contains the player key map
    :return: none
    """
    global rawHTML # global keyword allows access to the global variable
    if len(rawHTML) == 0:
        rawHTML[0] = IOKit.readIn(fileName='tempESPNBatters', ext=".html")
        rawHTML[1] = IOKit.readIn(fileName='tempESPNPitchers', ext=".html")
        

    soup = BeautifulSoup(rawHTML, 'lxml')
    # print(soup.prettify())
    global players
    # the specific "inline inline-table" class is the only one that contains the the positiional tables
    # DH table also uses "inline inline-with-table" class
    # If you need the the Top 300 use "inline inline-with-table" class
    className = re.compile("table$") 
    tables = soup.find_all("aside", class_=className)[1:] # the first table is the Top 300 so use range slicing to shred it
    for posGroup in tables:
        pos: str = posGroup.find("h2").text.split(" ", maxsplit=2)[2:][0] # slice off the first two words and then exit list
        playerRows = posGroup.find_all("tr")[1:] # the first row is the table header so use range slicing to shred it
        for player in playerRows:
            # column 1 is Pos Rank, 2 is Overall Rank, 3 is trend, 4 is Player, 5 is team, 6 is other pos, 7 is age
            playerData = player.find_all("td")
            espnID: str = playerData[3].find("a")["href"].split("/")[-2]
            # if espnID is a match in the player list, then update the player's position
            # else, create a new player and append it to the list
            p = next((p for p in players if p.espnID == espnID), None)
            if p is None:
                fangraphsID = df[df["ESPNID"] == espnID]["IDFANGRAPHS"].values[0]
                savantID = df[df["ESPNID"] == espnID]["MLBID"].values[0]
                players.append(Player().from_data(playerData, espnID, fangraphsID, savantID, pos))
            else:
                # update the player's position rank
                pass


            print(espnID)


    


def getFangraphsProjections(projSys: list[FGSystem] = (FGSystem.Steamer_RoS,), waitTime: int = 5):
    """
    Function that takes a requested projection system, builds URLs to match request, invokes Selenium to download the
    .csv, and renames the file according to the requested projection system
    :param waitTime: This is the hard wait time for the download to finish.  Over a slow network, the default value will
    time out too quickly and this value should increase.
    :param projSys: Projection System is an Enum that corresponds to an available projection system; reduces to a string
    :return: none
    """
    # ATC will only be used for preseason projections and thus placed in the appropriate directory
    if projSys == FGSystem.ATC:
        dirFG = dirHQ + "preseason/"
    else:
        dirFG = dirHQ + "regseason/"
    urls: list[dict] = DKFGLinkBuilder(projSys)
    for url in urls:
        sdrvr = DKDriverConfig(dirDownload=dirFG, headless=False)
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
            time.sleep(waitTime)
            # downloadWait = True
            # while downloadWait:
            #     for fname in os.listdir(dirFG):
            #         if fname.endswith('.crdownload'):
            #             downloadWait = True
            #         else: downloadWait = False
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
        IOKit.renameFile(dir=dirFG, fExt=".csv", downloadedFile=downloadedFile, newFileName=url["id"])


def getSavantData(statcastData: list[Savant], waitTime: int = 10):
    """
    Receives requested baseball savant data products, builds URLs to match request, invokes Selenium to download the
    .csv, and renames the file according to the dataset
    :param waitTime: This is the hard wait time for the download to finish.  Over a slow network, the default value will
    time out too quickly and this value should increase.
    :param statcastData: Savant enum representing the desired statcast data object
    :return: none
    """

    dirSvnt = dirHQ + "regseason/"
    savantDestinations: list[dict] = DKSavantLinkBuilder(statcast=statcastData)
    for dest in savantDestinations:
        sdrvr = DKDriverConfig(dirDownload=dirSvnt, headless=True)
        sdrvr.get(dest["url"])
        try:
            # Wait a reasonable time that a person would take
            sdrvr.implicitly_wait(15)
            # Wait until the element to download is available and then stop loading
            downloadBtn = sdrvr.find_element(By.ID, "btnCSV")
            time.sleep(3)
            downloadBtn.click()
            print("clicked 'Download CSV'")
            time.sleep(waitTime)
        except exceptions as e:
            sdrvr.close()
            print(e.message)
        sdrvr.close()

        IOKit.renameFile(dir=dirSvnt, fExt=".csv", downloadedFile=dest["download"], newFileName=dest["id"])


if __name__ == '__main__':
    leagueID = "10998"
    espnPlayerRaterURL = "https://fantasy.espn.com/baseball/playerrater?leagueId=" + leagueID
    playerKeyDatabaseURL = "https://docs.google.com/spreadsheets/d/1JgczhD5VDQ1EiXqVG-blttZcVwbZd5_Ne_mefUGwJnk/pubhtml?gid=0&single=true"

    dfKeyMap = fetchPlayerKeyMap(url=playerKeyDatabaseURL)
    getESPNPlyrUniverse(url=espnPlayerRaterURL)
    # buildPlayerUniverse(df=dfKeyMap)
    
    # TODO: Delete temporary files
    # TODO: Extract Fangraph pulls and Savant pulls into separate applet 
    # networkLatencyWaitTime = 10  # This value should be changes when the default times out due to slow network
    # getFangraphsProjections(projSys=[FGSystem.Steamer_RoS], waitTime=networkLatencyWaitTime)
    # getSavantData(statcastData=[Savant.xStats], waitTime=networkLatencyWaitTime)

