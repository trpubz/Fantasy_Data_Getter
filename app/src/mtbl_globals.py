# File with global variables
# by pubins.taylor
# v0.6.0
# lastUpdate 13 MAR 2024
from enum import Enum

DIR_EXTRACT = "/Users/Shared/BaseballHQ/resources/extract"
DIR_TRANSFORM = "/Users/Shared/BaseballHQ/resources/transform"
MTBL_KEYMAP_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEw6LWoxJrrBSFY39wA_PxSW5SG_t3J7dJT3JsP2DpMF5vWY6HJY071d8iNIttYDnArfQXg-oY_Q6I/pubhtml?gid=0&single=true"
# the names of the stat columns from Fangraphs downloaded csvs
HITTER_STATS = ["Name", "Team", "G", "PA", "HR", "R", "RBI", "SB", "CS", "BB%", "K%", "ISO",
                "BABIP", "AVG", "OBP", "SLG", "xSLG", "wOBA", "xwOBA", "wRC+", "wRAA", "EV",
                "Barrel%", "HardHit%", "PlayerId", "MLBAMID"]
PITCHER_STATS = ["Name", "Team", "G", "GS", "IP", "SV", "HLD", "ERA", "xERA", "WHIP", "FIP",
                 "xFIP", "SIERA", "K/9", "BB/9", "K/BB", "EV", "Barrel%", "HardHit%", "PlayerId",
                 "MLBAMID"]  # add QS during merge
# ESPN CONFIG
NO_MANAGERS = 11
LG_RULESET = {
    "ROSTER_SIZE": 21,
    "BENCH_SLOTS": 5,
    "DRAFT_BUDGET": 260,
    "SCORING": {
        "BATTING": [
            "R", "HR", "RBI", "SBN", "OBP", "SLG"
        ],
        "PITCHING": [
            "IP", "QS", "ERA", "WHIP", "KP9", "SVHD"
        ]
    }
}


class ETLType(Enum):
    PRE_SZN = "preseason"
    REG_SZN = "regular_season"

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return ETLType[s]
        except KeyError:
            raise ValueError()


class FGProjSys(Enum):
    DC_ROS = "rfangraphsdc"
    ZIPS_ROS = "rzips"
    STEAMER_ROS = "steamerr"
    ATC_DC_ROS = "ratcdc"
    BATX_ROS = "rthebatx"

    ATC = "atc"
    DC = "fangraphsdc"
    BATX = "thebatx"
    BAT = "thebat"


class FGStatGroup(Enum):
    # For Fantasy Stat Type
    FANTASY = "fantasy"
    ADVANCED = "advanced"
    STANDARD = "standard"
    DASHBOARD = "dashboard"


class FGFantasyPreset(Enum):
    # the default is dashboard if anything other than FGStatGroup.FANTASY is chosen
    DASHBOARD = "dashboard"
    CLASSIC = "classic"


class FGStats(Enum):
    # For in-season stats
    STD = "0"
    ADV = "1"
    STCST = "24"


class FGPosGrp(Enum):
    HIT = 'bat'
    PIT = 'pit'


class BRefStats(Enum):
    PIT = "starter-pitching"


class Savant(Enum):
    XSTATS = "expected_statistics"
    BARRELS = "statcast"
    ROLLING = "rolling"
    RANKINGS = "percentile-rankings"


class SavantDownload(Enum):
    XSTATS = "expected_stats.csv"
    BARRELS = "exit_velocity.csv"
    # rolling does not download .csv; need to webscrape
    RANKINGS = "percentile-rankings.csv"


class SavantPosGrp(Enum):
    HIT = "batter"
    PIT = "pitcher"
