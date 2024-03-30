"""
Automates the gathering of useful Fantasy Baseball Player Data.
Pulls regular season stats for the ESPN Fantasy Universe from the league's Player Rater page.
Pull preseason projections from the league's Projections page.
v 4.0.0
modified: 15 MAR 2024
by pubins.taylor
"""
import os
import argparse
import shutil

from app.src.scrape import Scraper
import app.src.build as build

from mtbl_driverkit.mtbl_driverkit import TempDirType

from app.src.mtbl_globals import ETLType

ESPN_PLAYER_RATER_BASE_URL = "https://fantasy.espn.com/baseball/playerrater?leagueId="
ESPN_PROJECTIONS_BASE_URL = "https://fantasy.espn.com/baseball/players/projections?leagueId="


def delete_temp_files():
    """
    Function that deletes the temp files that were created during the execution of the program
    :return: none
    """
    project_root = os.path.abspath(os.path.dirname(__file__))  # Get directory of 'app/__main__.py'
    temp_path = os.path.join(project_root, "temp")

    if os.path.exists(temp_path):  # Check if "temp" folder exists
        shutil.rmtree(temp_path)


def main(lg_id, etl_type):
    print("\n---Running Fantasy Data Getter---\n")
    url = ""
    match etl_type:
        case ETLType.PRE_SZN:
            url = ESPN_PROJECTIONS_BASE_URL
        case ETLType.REG_SZN:
            url = ESPN_PLAYER_RATER_BASE_URL
    url += lg_id

    # handle app directory
    project_root = os.path.abspath(os.path.dirname(__file__))
    temp_path = os.path.join(project_root, "temp")
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    scraper = Scraper((TempDirType.APP, temp_path), etl_type=etl_type,
                      headless=False)
    scraper.get_espn_plyr_universe(url)

    raw_html = []
    match etl_type:
        case ETLType.PRE_SZN:
            raw_html = [scraper.bats, scraper.arms]
        case ETLType.REG_SZN:
            raw_html = [scraper.combined_table]

    # Parse the raw html into players
    build.build_player_universe(etl_type, raw_html)

    delete_temp_files()

    print("\n---Finished Fantasy Data Getter---")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process Fantasy Universe Data")
    parser.add_argument(
        "--lgID",
        type=str, help="League ID",
        default=os.getenv("MTBL_LGID", 'default value'))
    parser.add_argument(
        "--etl-type",
        type=ETLType.from_string,
        choices=list(ETLType),
        help="ETL Type; PRE_SZN or REG_SZN",
        default=ETLType.REG_SZN)

    args = parser.parse_args()
    main(args.lgID, args.etl_type)
