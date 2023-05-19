# WHAT WE DOIN HERE
# by pubins.taylor
# v0.1
# created DD MMM YYYY
# lastUpdate DD MMM YYYY

from enum import Enum


dirHQ = "/Users/Shared/BaseballHQ/resources/extract"


class FGSystem(Enum):
    DC_RoS = "rfangraphsdc"
    ZiPS_RoS = "rzips"
    Steamer_RoS = "steamerr"
    ATC = "atc"


class FGPosGrp(Enum):
    HIT = 'bat'
    PIT = 'pit'


class Savant(Enum):
    xStats = "expected_statistics"
    barrels = "statcast"
    rolling = "rolling"
    rankings = "percentile-rankings"


class SavantDownload(Enum):
    xStats = "expected_stats.csv"
    barrels = "exit_velocity.csv"
    # rolling does not download .csv; need to webscrape
    rankings = "percentile-rankings.csv"


class SavantPosGrp(Enum):
    HIT = "batter"
    PIT = "pitcher"
