# Fantasy_Data_Getter
Retrieves only relevant ESPN Player Universe from the league's Player Rater first handlful of pages.

## Dependancies
- espnPlayerRaterURL = "https://fantasy.espn.com/baseball/playerrater?leagueId=" + leagueID
- Player Key Map reference from [here]("https://docs.google.com/spreadsheets/d/e/2PACX-1vSEw6LWoxJrrBSFY39wA_PxSW5SG_t3J7dJT3JsP2DpMF5vWY6HJY071d8iNIttYDnArfQXg-oY_Q6I/pubhtml?gid=0&single=true")
  - database is managed by @trpubz

## Outputs
- espnPlayerUniverse.json
  - .json schema is: 
```
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "_name": {
        "type": "string"
      },
      "firstName": {
        "type": "string"
      },
      "idESPN": {
        "type": "string"
      },
      "idFangraphs": {
        "type": "string"
      },
      "lastName": {
        "type": "string"
      },
      "pos": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "suffix": {
        "type": "string"
      },
      "tm": {
        "type": "string"
      }
    },
    "required": ["_name", "firstName", "idESPN", "lastName", "pos", "tm"]
  }
}
```
