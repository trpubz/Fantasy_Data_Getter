"""
Parse Player Universe from raw HTML string
v0.1.0
modified: 27 FEB 2024
by pubins.taylor
"""
import os
import re
from typing import List

from bs4 import BeautifulSoup
from mtbl_playerkit import ESPNPlayer

from app.src.mtbl_globals import ETLType, DIR_EXTRACT
from mtbl_iokit import write, read
from mtbl_iokit.read import IOKitDataTypes
from mtbl_playerkit.espn_player import ESPNPlayer

from .mtbl_globals import ETLType

players: list[ESPNPlayer] = []


def build_player_universe(etl_type: ETLType,
                          raw_html: list = None,
                          temp_dir: any = None,
                          output_dir: str = DIR_EXTRACT) -> None:
    """
    Function that parses the ESPN Fantasy Universe HTML file and extracts the player names and their
    ESPN Player IDs. This function is dependent on the ESPN Fantasy Universe HTML file being
    downloaded and saved to the project root.
    :param etl_type: PRESZN or REGSZN
    :param raw_html: list containing the raw HTMLs
    :param temp_dir: string containing the path to raw HTML file.
                        if None, raw_html must not be None.
    :param output_dir: string containing the directory to save json
    :return: none
    """
    os.environ['PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT'] = '1.5s'

    if raw_html is None:
        try:
            raw_html = stringify_raw_html(temp_dir, etl_type)
        except RawHtmlLoadError as e:
            print(f"Could not load raw HTML file. {e}")
            exit(1)

    global players

    for group in raw_html:
        if isinstance(group, str):
            soup = BeautifulSoup(group, 'lxml')
        else:  # it may be passed in as bs4.element.Tag
            soup = group

        player_rows = soup.find_all("tr")
        # first row is designated by the "th" tag, so no need to skip it here
        for player in player_rows:
            player_data = player.find_all("td")
            # shohei player id is 39382
            player = ESPNPlayer.from_data(player_data, etl_type)
            players.append(player)

    # save the player universe to a json file
    write.write_out(players, output_dir, "espn_player_universe", ".json")


def stringify_raw_html(temp_dir, etl_type: ETLType) -> list:
    """
    Loads raw HTML files from directory
    :param temp_dir: where to locate files
    :param etl_type: PRESZN or REGSZN
    :return: list of raw htmls
    """
    if temp_dir is None:
        raise RawHtmlLoadError("raw_html cannot be empty and temp_dir None")

    match etl_type:
        case ETLType.REG_SZN:
            return [read.read_in_as(temp_dir,
                                    'temp_espn_player_universe',
                                    ".html",
                                    IOKitDataTypes.STR)]
        case ETLType.PRE_SZN:
            return [read.read_in_as(temp_dir,
                                    'temp_espn_bats_universe',
                                    ".html",
                                    IOKitDataTypes.STR),
                    read.read_in_as(temp_dir,
                                    'temp_espn_arms_universe',
                                    ".html",
                                    IOKitDataTypes.STR)
                    ]


class RawHtmlLoadError(Exception):
    pass
