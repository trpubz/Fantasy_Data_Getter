# File with global variables
# by pubins.taylor
# v0.3.0
# lastUpdate 27 FB 2024
from enum import Enum


DIR_EXTRACT = "/Users/Shared/BaseballHQ/resources/extract"


class FGSystem(Enum):
    DC_ROS = "rfangraphsdc"
    ZIPS_ROS = "rzips"
    STEAMER_ROS = "steamerr"
    ATC = "atc"


class FGPosGrp(Enum):
    HIT = 'bat'
    PIT = 'pit'


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
