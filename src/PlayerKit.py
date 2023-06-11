"""
Description: PlayerKit is a module that contains the abstracts the player creation from the main executable
by pubins.taylor
version: 1.0.1
date created: 19 MAY 2023
date modified: 08 JUN 2023
"""
import re

import bs4
from bs4 import BeautifulSoup


# a class that represents a player, the attributes need to include the following: name, position dictionary,
# ESPN ID, Fangraphs ID, team, age


class Player:
    def __init__(self, name="", team="", ovr: int = 0, positions=[], owner="", playerRater={}, espnID="",
                 fangraphsID="", savantID=""):
        self._name: str = name
        self.team: str = team
        self.ovr: int = ovr
        self.positions: list = positions
        self.owner: str = owner
        self.playerRater: dict = playerRater
        self.espnID = espnID
        self.fangraphsID: str = fangraphsID
        self.savantID: str = savantID

    @classmethod
    def from_data(cls, data: list, espnID: str, fangraphsID: str, savantID: str):
        name = data[1].find("a", class_="AnchorLink").get_text(strip=True)
        ovr = int(data[0].text)
        regexPos = re.compile(".*playerpos.*")
        positions: list = data[1].find("span", class_=regexPos).get_text(strip=True).split(", ")
        regexTm = re.compile(".*playerteam.*")
        team = data[1].find(class_=regexTm).get_text(strip=True).upper()
        # if the owner is not listed, then the player is a free agent and the splitting the text will drop the waiver
        # date and return only WA
        owner = data[2].get_text(strip=True).split(" ")[0]
        playerRater = addPlayerRaterData(data[3:], positions)

        return cls(name=name, ovr=ovr, positions=positions, team=team, owner=owner, playerRater=playerRater,
                   espnID=espnID, fangraphsID=fangraphsID, savantID=savantID)

    def to_dict(self):
        return {
            '_name': self._name,
            'team': self.team,
            'ovr': self.ovr,
            'positions': self.positions,
            'owner': self.owner,
            'playerRater': self.playerRater,
            'espnID': self.espnID,
            'fangraphsID': self.fangraphsID,
            'savantID': self.savantID
        }


def addPlayerRaterData(data: list, positions: list) -> dict[str: float]:
    playerRater = {}
    for d in data:
        cat = ""
        try:
            cat = d.find("div")["title"]
        except KeyError:  # indicates no title attribute is found
            continue
        if any(p for p in positions if "SP" not in p or "RP" not in p):
            match cat:
                case "Runs Scored":
                    playerRater.update({"R": float(d.get_text(strip=True))})
                    continue
                case "Home Runs":
                    playerRater.update({"HR": float(d.get_text(strip=True))})
                    continue
                case "Runs Batted In":
                    playerRater.update({"RBI": float(d.get_text(strip=True))})
                    continue
                case "Net Stolen Bases":
                    playerRater.update({"SBN": float(d.get_text(strip=True))})
                    continue
                case "On Base Pct":
                    playerRater.update({"OBP": float(d.get_text(strip=True))})
                    continue
                case "Slugging Pct":
                    playerRater.update({"SLG": float(d.get_text(strip=True))})
                    continue
        if any(p for p in positions if "SP" in p or "RP" in p):
            match cat:
                case "Innings Pitched":
                    playerRater.update({"IP": float(d.get_text(strip=True))})
                    continue
                case "Quality Starts":
                    playerRater.update({"QS": float(d.get_text(strip=True))})
                    continue
                case "Earned Run Average":
                    playerRater.update({"ERA": float(d.get_text(strip=True))})
                    continue
                case "Walks plus Hits Per Innings Pitched":
                    playerRater.update({"WHIP": float(d.get_text(strip=True))})
                    continue
                case "Strikeouts per 9 Innings":
                    playerRater.update({"K/9": float(d.get_text(strip=True))})
                    continue
                case "Saves Plus Holds":
                    playerRater.update({"SVHD": float(d.get_text(strip=True))})
                    continue
        match cat:
            case _ if re.match(".*rostered.*", cat):
                playerRater.update({"%ROST": float(d.get_text(strip=True))})
            case _ if re.match(".*Rating.*", cat):
                try:
                    playerRater.update({"PRTR": float(d.get_text(strip=True))})
                except ValueError:  # will raise if the player rater is "--"
                    playerRater.update({"PRTR": 0.0})

    return playerRater