"""
Automates the gathering of useful Fantasy Baseball Player Data.
Exclusively the ESPN Fantasy Universe from the league's Player Rater page.
v 2.0.0
modified: 03 AUG 2023
by pubins.taylor
"""
from time import sleep
import re
import os
import subprocess

from scrape import *
import src.IOKit as IOKit
from src.Globals import dirHQ
from src.PlayerKit import Player

from bs4 import BeautifulSoup
import pandas as pd

rawHTML: str = ""
players: list[Player] = []


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
        # # print(df)
        # print(f"found {filename}, returning dataframe")
        return df
    except FileNotFoundError:
        # TODO: import this module from package
        # fetch the data with the MTBL_KeyMap script
        key_map_dir = "/Users/Shared/BaseballHQ/tools/MTBL_KeyMap/"
        subprocess.run([key_map_dir + ".venv/bin/python3",
                        key_map_dir + "main.py"])
        fetchPlayerKeyMap()


def buildPlayerUniverse(dfKeyMap: pd.DataFrame):
    """
    Function that parses the ESPN Fantasy Universe HTML file and extracts the player names and their ESPN Player IDs.
    This function is dependent on the ESPN Fantasy Universe HTML file being downloaded and saved to the project root.
    :param dfKeyMap: pandas dataframe that contains the player key map
    :return: none
    """
    os.environ['PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT'] = '1.5s'
    # print("Building player universe from raw HTML")
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

    # print(f"Finished building player universe.  {len(players)} players found.")

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

    # print("\n---Running Fantasy Data Getter---\n")

    dfKeyMap = fetchPlayerKeyMap()
    # check to see if tempESPNPlayerRater.html exists; if not, download it
    if not os.path.exists("tempESPNPlayerUniverse.html"):
        global rawHTML
        rawHTML = getESPNPlyrUniverse(url=espnPlayerRaterURL, headless=False)

    buildPlayerUniverse(dfKeyMap=dfKeyMap)

    deleteTempFiles()

    # print("\n---Finished Fantasy Data Getter---")


if __name__ == '__main__':
    main()
