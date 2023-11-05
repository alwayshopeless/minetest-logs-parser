# Minetest log parser
Simple parser for Minetest logs. Parse Minetest logs to JSON.

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
        print(parsedLog)
```
