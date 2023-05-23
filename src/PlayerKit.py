"""
Description: PlayerKit is a module that contains the abstracts the player creation from the main executable
by pubins.taylor
version: 0.0.1
date created: 19 MAY 2023
date modified: 19 MAY 2023
"""
import re

from bs4 import BeautifulSoup


# TODO: player position should be a list object or maybe a dictionary object with the key being the position and the value being the position rank

# create a class that represents a player, the attributes need to inclue the following: name, position dictionary, ESPN ID, Fangraphs ID, team, age 

class Player:
    def __init__(self, name = "", team = "", ovr: int = 0, positions = [], owner = "", playerRater = {}, espnID = "", fangraphsID = "", savantID = ""):
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
        # create a match statement to convert the pos string to an abbreviation
        # match pos:
        #     case "Catchers": pos = "C"
        #     case "First Basemen": pos = "1B"
        #     case "Second Basemen": pos = "2B"
        #     case "Third Basemen": pos = "3B"
        #     case "Shortstops": pos = "SS"
        #     case "Outfields": pos = "OF"
        #     case "Designated Hitters": pos = "DH"
        #     case "Starting Pitchers": pos = "SP"
        #     case "Relief Pitchers": pos = "RP"

        name = data[1].find("a", class_="AnchorLink").get_text(strip=True)
        ovr = int(data[0].text)
        reg = re.compile(".*playerpos.*")
        positions: list = data[1].find("span", class_=reg).get_text(strip=True).split(", ")
        reg = re.compile(".*playerteam.*")
        team = data[1].find(class_=reg).get_text(strip=True).upper()
        owner = data[2].get_text(strip=True).split(" ")[0] # if the owner is not listed, then the player is a free agent and the splitting the text will drop the waiver date and return only WA
        if not any(p for p in positions if p.__contains__("P")):
            playerRater = {
                "R": float(next(i for i in data if i.find("div", {"title": "Runs Scored"})).get_text(strip=True)),
                "HR": float(next(i for i in data if i.find("div", {"title": "Home Runs"})).get_text(strip=True)),
                "RBI": float(next(i for i in data if i.find("div", {"title": "Runs Batted In"})).get_text(strip=True)),
                "SBN": float(next(i for i in data if i.find("div", {"title": "Net Stolen Bases"})).get_text(strip=True)),
                "OBP": float(next(i for i in data if i.find("div", {"title": "On Base Pct"})).get_text(strip=True)),
                "SLG": float(next(i for i in data if i.find("div", {"title": "Slugging Pct"})).get_text(strip=True)),
            }
        else:
            playerRater = {
                "IP": float(next(i for i in data if i.find("div", {"title": "Innings Pitched"})).get_text(strip=True)),
                "QS": float(next(i for i in data if i.find("div", {"title": "Quality Starts"})).get_text(strip=True)),
                "ERA": float(next(i for i in data if i.find("div", {"title": "Earned Run Average"})).get_text(strip=True)),
                "WHIP": float(next(i for i in data if i.find("div", {"title": "Walks plus Hits Per Innings Pitched"})).get_text(strip=True)),
                "K/9": float(next(i for i in data if i.find("div", {"title": "Strikeouts per 9 Innings"})).get_text(strip=True)),
                "SVHD": float(next(i for i in data if i.find("div", {"title": "Saves Plus Holds"})).get_text(strip=True)),
            }
        playerRater["%ROS"] = float(next(i for i in data if i.find("div", {"title": re.compile(".*rostered.*")})).get_text(strip=True))
        playerRater["PRTR"] = float(next(i for i in data if i.find("div", {"title": re.compile(".*Rating.*")})).get_text(strip=True))

        return cls(name, ovr, positions, team, owner, playerRater, espnID, fangraphsID, savantID)
    
    def add_position(self, data: any, pos: str):
        # create a match statement to convert the pos string to an abbreviation
        match pos:
            case "Catcher": pos = "C"
            case "First Base": pos = "1B"
            case "Second Base": pos = "2B"
            case "Third Base": pos = "3B"
            case "Shortstop": pos = "SS"
            case "Outfield": pos = "OF"
            case "Designated Hitter": pos = "DH"
            case "Starting Pitcher": pos = "SP"
            case "Relief Pitcher": pos = "RP"

        self.position[pos] = int(data.select_one('selector_for_position_rank').text)
    
