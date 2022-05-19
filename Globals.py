# WHAT WE DOIN HERE
# by pubins.taylor
# v0.1
# created DD MMM YYYY
# lastUpdate DD MMM YYYY

from enum import Enum


dirHQ = "/Users/Shared/BaseballHQ/"


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


class SavantDownload(Enum):
    xStats = "expected_stats.csv"


class SavantPosGrp(Enum):
    HIT = "batter"
    PIT = "pitcher"
