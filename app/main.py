"""
Automates the gathering of useful Fantasy Baseball Player Data.
Exclusively the ESPN Fantasy Universe from the league's Player Rater page.
v 3.0.0
modified: 1 FEB 2024
by pubins.taylor
"""
import os
import argparse

import src.scrape as scrape
import src.IOKit as IOKit
from src.Globals import dirHQ
from src.PlayerKit import Player

from bs4 import BeautifulSoup

players: list[Player] = []
ESPN_PLAYER_RATER_BASE_URL = "https://fantasy.espn.com/baseball/playerrater?leagueId="


def buildPlayerUniverse(raw_html):
    """
    Function that parses the ESPN Fantasy Universe HTML file and extracts the player names and their
    ESPN Player IDs. This function is dependent on the ESPN Fantasy Universe HTML file being
    downloaded and saved to the project root.
    :param raw_html: string containing the raw HTML file
    :return: none
    """
    os.environ['PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT'] = '1.5s'

    if raw_html == "":
        raw_html = IOKit.readIn(fileName='tempESPNPlayerUniverse', ext=".html")

    soup = BeautifulSoup(raw_html, 'lxml')
    # print(soup.prettify())
    global players

    playerRows = soup.find_all("tr")

    for player in playerRows:  # first row is designated by the "th" tag, so no need to skip it here
        playerData = player.find_all("td")
        # location ID can be in either the src or data-src attribute
        # if both are present, then data-src is the one to use
        idLoc: str = (playerData[1].find("img").get("data-src")
                      or
                      playerData[1].find("img").get("src"))
        try:
            espnID = re.findall(r'full/(\d+)\.png', idLoc)[0]
        except Exception as e:
            print(f"cannot find espnID in html for {playerData[1].get_text(strip=True)}.  Error message: {e}")
            continue
        # shohei player id is 39382
        try:
            players.append(Player().from_data(playerData, espnID))
        except IndexError as ie:
            print(f"Error occurred while processing {playerData[1].get_text(strip=True)}: {espnID}. \n"
                  f"   No matching player found in the key map")
            pctRostered = float(playerData[16].get_text(strip=True))
            if pctRostered > 2.0:
                print(f"   player is rostered {pctRostered} \
                      of leagues, update/add player to key map!")
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


def main(lg_id):
    print("\n---Running Fantasy Data Getter---\n")

    raw_html = ""
    if not os.path.exists("temp_espn_player_universe.html"):
        # Fetch the raw html if a temp file does not exist
        raw_html = scrape.get_espn_plyr_universe(
            url=ESPN_PLAYER_RATER_BASE_URL + lg_id,
            headless=False)

    # Parse the raw html into players
    buildPlayerUniverse(raw_html)

    deleteTempFiles()

    print("\n---Finished Fantasy Data Getter---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process league ID.")
    parser.add_argument(
        "--lgID",
        type=str, help="League ID",
        default=os.getenv("MTBL_LGID", 'default value'))

    args = parser.parse_args()
    main(args.lgID)
