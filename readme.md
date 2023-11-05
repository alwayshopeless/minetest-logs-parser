# Minetest log parser
Simple parser for Minetest logs. Parses Minetest logs to JSON.

## Description
It only asks for player actions on the server, including authorization and events such as digs, places, moves, actives, punched etc.

## Using
Simple example:

```python
from src.Parser.MinetestLogParser import MinetestLogParser

if __name__ == '__main__':
    input = "./debug.txt"
    minetestParser = MinetestLogParser(input)

    for parsedLog in minetestParser.read():
        playerNames = ['littlePrettyCat', 'Melon', 'Player']
        if parsedLog['name'] in playerNames:
            print(parsedLog)
```
Parsed line output examples:

Action:
```json
{"timestamp": 1698474247, "name": "Player", "action": "places node", "meta_action": null, "node": "default:dirt", "count": 1, "coords": null, "type": null, "logType": "action"}
```
Beowulf auth:
```json
{"timestamp": 1698471091, "name": "Player", "ip": "127.0.0.1", "protocolVersion": "40", "formspecVersion": "4", "lang": "en", "logType": "beowulfAuth"}
```
Default auth:
```json
{"timestamp": 1698471091, "name": "Player", "ip": "127.0.0.1", "logType": "auth"}

```
