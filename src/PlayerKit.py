"""
Description: PlayerKit is a module that contains the abstracts the player creation from the main executable
by pubins.taylor
version: 0.0.1
date created: 19 MAY 2023
date modified: 19 MAY 2023
"""
# TODO: player position should be a list object or maybe a dictionary object with the key being the position and the value being the position rank

# create a class that represents a player, the attributes need to inclue the following: name, position dictionary, ESPN ID, Fangraphs ID, team, age 

class Player:
    def __init__(self, name = "", position = {"":""}, espnID = "", fangraphsID = "", savantID = "", team = "", age: int = 99):
        self._name: str = name
        self.team: str = team
        self.position: dict = position
        self.espnID = espnID
        self.fangraphsID: str = fangraphsID
        self.savantID: str = savantID
        self.age: int = age

    @classmethod
    def from_data(cls, data: any, espnID: str, fangraphsID: str, savantID: str, pos: str):
        # create a match statement to convert the pos string to an abbreviation
        match pos:
            case "Catchers": pos = "C"
            case "First Basemen": pos = "1B"
            case "Second Basemen": pos = "2B"
            case "Third Basemen": pos = "3B"
            case "Shortstops": pos = "SS"
            case "Outfields": pos = "OF"
            case "Designated Hitters": pos = "DH"
            case "Starting Pitchers": pos = "SP"
            case "Relief Pitchers": pos = "RP"

        name = data.select_one('selector_for_name').text
        position: dict = {pos: int(data.select_one('selector_for_position_rank').text)}
        espnID = data.select_one('selector_for_espn_id').text

        team = data.select_one('selector_for_team').text

        age = int(data.select_one('selector_for_age').text)  # Assume age is an integer

        return cls(name, position, espnID, fangraphsID, savantID, team, age)
    
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
    
