# Fantasy_Data_Getter
retrieves all relevant Fantasy Data (ESPN Player Universe, Fangraphs Projections, Baseball Savant Data)

## Dependancies
- URL for ESPN's Top 300 Player
- FG [url?]
- BS [url?]

## Outputs
- shaved down .html of ESPN's Top 300 Players for later processing by a [diff app](https://github.com/trpubz/ESPN_FantasyPlayerList)
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
- .csv from Fangraphs
- .csv from baseball savant
