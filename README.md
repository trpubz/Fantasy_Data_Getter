# Fantasy Data Getter
Retrieves only relevant ESPN Player Universe from the league's Player Rater first handlful of pages.

## Dependencies
- espnPlayerRaterURL = "https://fantasy.espn.com/baseball/playerrater?leagueId=" + leagueID
- This package saves data to `dirHQ = "/Users/Shared/BaseballHQ/resources/extract"` which can be updated in `[Globals.py]`
- Player Key Map reference from [here](https://docs.google.com/spreadsheets/d/e/2PACX-1vSEw6LWoxJrrBSFY39wA_PxSW5SG_t3J7dJT3JsP2DpMF5vWY6HJY071d8iNIttYDnArfQXg-oY_Q6I/pubhtml?gid=0&single=true)
  - database is managed by @trpubz

## Outputs
- espnPlayerUniverse.json
  - .json schema is: 
```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": [
        {
            "type": "object",
            "properties": {
                "_name": { "type": "string" },
                "team": { "type": "string" },
                "ovr": { "type": "integer" },
                "positions": {
                    "type": "array",
                    "items": [
                        { "type": "string" }
                    ]
                },
                "owner": { "type": "string" },
                "playerRater": {
                    "type": "object",
                    "properties": {
                        "R": { "type": "number" },
                        "HR": { "type": "number" },
                        "RBI": { "type": "number" },
                        "SBN": { "type": "number" },
                        "OBP": { "type": "number" },
                        "SLG": { "type": "number" },
                        "%ROS": { "type": "number" },
                        "PRTR": { "type": "number" }
                    },
                    "required": [
                        "%ROS",
                        "PRTR"
                    ]
                },
                "espnID": { "type": "string" },
                "fangraphsID": { "type": "string" },
                "savantID": { "type": "string" }
            },
            "required": [
                "_name",
                "team",
                "ovr",
                "positions",
                "owner",
                "playerRater",
                "espnID",
                "fangraphsID",
                "savantID"
            ]
        }
    ]
}
```
