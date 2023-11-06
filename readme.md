# Minetest log parser
Simple parser for Minetest logs. Parses Minetest logs to JSON.

## Description
It only asks for player actions on the server, including authorization and events such as digs, places, moves, actives, punched etc.

## Installing
Clone repository or use pip for install minetest-log-parser 
```bash
pip install minetest-log-parser
```

## Using
Simple example reading via generator parsed dicts:

```python
from minetest_log_parser.Parser.MinetestLogParser import MinetestLogParser

if __name__ == '__main__':
    input = "./debug.txt"
    minetestParser = MinetestLogParser(input)

    for parsedLog in minetestParser.read():
        playerNames = ['littlePrettyCat', 'Melon', 'Player']
        if parsedLog['name'] in playerNames:
            print(parsedLog)
```
Example for import logs to JSON:

```python
from minetest_log_parser.Parser.MinetestLogParser import MinetestLogParser

if __name__ == '__main__':
    input = "./debug.txt"
    output = "./debug.json"
    minetestParser = MinetestLogParser(input)

    minetestParser.importToJson(output)
```
## Parsed line output examples:

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
