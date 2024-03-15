"""
Parse Player Universe from raw HTML string
v0.1.0
modified: 27 FEB 2024
by pubins.taylor
"""
import os
import re
from bs4 import BeautifulSoup
from app.src.mtbl_globals import ETLType, DIR_EXTRACT
from mtbl_iokit import write, read
from mtbl_iokit.read import IOKitDataTypes
from mtbl_playerkit.espn_player import ESPNPlayer

from .mtbl_globals import ETLType

players: list[ESPNPlayer] = []


def build_player_universe(etl_type: ETLType,
                          raw_html: str = "",
                          temp_dir: any = None,
                          output_dir: str = DIR_EXTRACT) -> None:
    """
    Function that parses the ESPN Fantasy Universe HTML file and extracts the player names and their
    ESPN Player IDs. This function is dependent on the ESPN Fantasy Universe HTML file being
    downloaded and saved to the project root.
    :param etl_type: PRESZN or REGSZN
    :param raw_html: string containing the raw HTML file
    :param temp_dir: string containing the path to raw HTML file.
                        if None, raw_html must not be None.
    :param output_dir: string containing the directory to save json
    :return: none
    """
    os.environ['PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT'] = '1.5s'

    if raw_html == "":
        try:
            raw_html = stringify_raw_html(temp_dir)
        except RawHtmlLoadError as e:
            print(f"Could not load raw HTML file. {e}")
            exit(1)

    soup = BeautifulSoup(raw_html, 'lxml')
    # print(soup.prettify())
    global players

    player_rows = soup.find_all("tr")

    for player in player_rows:  # first row is designated by the "th" tag, so no need to skip it here
        player_data = player.find_all("td")
        # shohei player id is 39382
        try:
            player = ESPNPlayer.from_data(player_data)
            players.append(player)
        except IndexError as ie:
            print(
                f"Error occurred while processing {player_data[1].get_text(strip=True)}: {espn_id}. \n"
                f"   No matching player found in the key map")
            pct_rostered = float(player_data[16].get_text(strip=True))
            if pct_rostered > 2.0:
                print(f"   player is rostered {pct_rostered} \
                      of leagues, update/add player to key map!")
            continue

    # print(f"Finished building player universe.  {len(players)} players found.")
    # save the player universe to a json file
    write.write_out(players, output_dir, "espn_player_universe", ".json")


def stringify_raw_html(temp_dir) -> str:
    if temp_dir is None:
        raise RawHtmlLoadError("raw_html cannot be empty and temp_dir None")

    return read.read_in_as(temp_dir,
                           'temp_espn_player_universe',
                           ".html",
                           IOKitDataTypes.STR)


class RawHtmlLoadError(Exception):
    pass
