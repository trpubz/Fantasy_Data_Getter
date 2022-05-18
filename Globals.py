# WHAT WE DOIN HERE
# by pubins.taylor
# v0.1
# created DD MMM YYYY
# lastUpdate DD MMM YYYY

from enum import Enum


dirHQ = "/Users/Shared/BaseballHQ/"


class Projections(Enum):
    DC_RoS = "rfangraphsdc"
    ZiPS_RoS = "rzips"
    Steamer_RoS = "steamerr"
    ATC = "atc"


class StatGrp(Enum):
    HIT = 'bat'
    PIT = 'pit'
