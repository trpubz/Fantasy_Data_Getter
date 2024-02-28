"""
Automates the gathering of useful Fantasy Baseball Player Data.
Exclusively the ESPN Fantasy Universe from the league's Player Rater page.
v 3.0.0
modified: 27 FEB 2024
by pubins.taylor
"""
import os
import argparse

import src.scrape as scrape
import src.build as build

from mtbl_driverkit.mtbl_driverkit import TempDirType


ESPN_PLAYER_RATER_BASE_URL = "https://fantasy.espn.com/baseball/playerrater?leagueId="


def delete_temp_files():
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

    # handle app directory
    project_root = os.path.abspath(os.path.dirname(__file__))
    temp_path = os.path.join(project_root, "temp")
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    raw_html = ""
    if not os.path.exists(os.path.join(temp_path, "temp_espn_player_universe.html")):
        # Fetch the raw html if a temp file does not exist
        raw_html = scrape.get_espn_plyr_universe(
            (TempDirType.APP, temp_path),
            url=ESPN_PLAYER_RATER_BASE_URL + lg_id,
            headless=False)

    # Parse the raw html into players
    build.build_player_universe(raw_html)

    delete_temp_files()

    print("\n---Finished Fantasy Data Getter---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process league ID.")
    parser.add_argument(
        "--lgID",
        type=str, help="League ID",
        default=os.getenv("MTBL_LGID", 'default value'))

    args = parser.parse_args()
    main(args.lgID)
