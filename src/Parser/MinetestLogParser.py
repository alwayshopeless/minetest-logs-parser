import json
import re
from datetime import datetime
from enum import Enum
from typing import Optional

from src.Helpers.stringHelpers import findStringBetween, extractCoords


def buildLog(logDict, logType):
    if logDict is None:
        return None

    logDict['logType'] = logType
    return logDict


logType = {
    'beowulfAuth': 'beowulfAuth',
    'auth': 'auth',
    'action': 'action',
}


class MinetestLogParser:
    logFilepath = ''
    actionPlaceholder = 'ACTION[Server]'
    beowulfPlaceholder = '[beowulf] player'
    defaultAuthPlaceholer = 'joins game.'

    def __init__(self, logFilepath):
        if logFilepath != '' and logFilepath != None:
            self.logFilepath = logFilepath

    def read(self):
        for line in self.rawReader():
            parsedLine = self.commonLineHandler(line)
            if parsedLine is None:
                continue
            yield parsedLine
        return None

    def rawReader(self):
        with open(self.logFilepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if len(line) == 0:
                    continue
                yield line

    def readAll(self):
        logs = []
        for line in self.rawReader():
            res = self.commonLineHandler(line)
            if res is not None:
                logs.append(res)

    def importToLineSeparatedJson(self, newLogFilePath):
        with open(newLogFilePath, 'w+', encoding='utf-8') as f:
            for parsedLine in self.read():
                if parsedLine is not None:
                    f.write(json.dumps(parsedLine))

    def importToJson(self, newLogFilePath):
        with open(newLogFilePath, 'w+', encoding='utf-8') as f:
            f.write("[")
            first_item = True
            for parsedLine in self.read():
                if parsedLine is not None:
                    if not first_item:
                        f.write(",")
                    f.write(json.dumps(parsedLine))
                    first_item = False
            f.write("]")

    @classmethod
    def commonLineHandler(cls, line: str) -> Optional[list]:
        # first, filter logs by server action
        # 2023-10-31 13:47:20: ACTION[Server]:
        if not cls.isServerActionLog(line):
            return None

        line = cls.cleanActionLogString(line)

        if cls.beowulfPlaceholder in line:
            # parse default anticheat authlog
            return buildLog(cls.parseBeowulfLine(line), logType["beowulfAuth"])

        elif cls.defaultAuthPlaceholer in line:
            # parse default auth log string
            return buildLog(cls.parseDefaultAuthLine(line), logType["auth"])

        else:
            # parse player action log string
            return buildLog(cls.parseActionLine(line), logType["action"])

    @classmethod
    def isServerActionLog(cls, line):
        if len(line) < 29:
            return False
        if line[21] != 'A' and line[28] != 'S':
            return False

        return True

    @classmethod
    def parseBeowulfLine(cls, line: str) -> Optional[dict]:
        if line is None:
            return None

        res = cls.extractTimestampAndAction(line)

        if res is not None:
            [timestamp, actionPart] = res
        else:
            return None

        try:
            rawAction = actionPart.split("[beowulf] player '", 1)
            if len(rawAction) != 2:
                print('Wrong auth string')
                print(actionPart)
                return None
            [name, other] = rawAction[1].split("' joined from ", 1)
            [ip, other] = other.split(" protocol_version: ", 1)
            [protocolVersion, other] = other.split(" formspec_version: ", 1)
            protoAndLang = other.split(" lang_code:", 1)
            formspecVersion = protoAndLang[0]
            if len(protoAndLang) == 1:
                lang = ''
            else:
                lang = protoAndLang[1].replace(" lang_code: ", '').strip()
        except Exception:
            print('Parsing error')
            print(Exception.__traceback__)
            return None
        return {
            "timestamp": timestamp,
            "name": name,
            "ip": ip,
            "protocolVersion": protocolVersion,
            "formspecVersion": formspecVersion,
            "lang": lang,
        }

    @classmethod
    def parseDefaultAuthLine(cls, line: str) -> Optional[dict]:
        if line is None:
            return None

        res = cls.extractTimestampAndAction(line)

        if res is not None:
            [timestamp, actionPart] = res
        else:
            return None

        pattern = r"(\w+) \[([\d.]+)\] joins game\."
        match = re.search(pattern, actionPart)

        if match:
            playerName = match.group(1)
            ipAddress = match.group(2)
        else:
            return None
        return {
            "timestamp": timestamp,
            "name": playerName,
            "ip": ipAddress,
        }

    @classmethod
    def parseActionLine(cls, line):
        count = 1
        action = None
        meta_action = None
        node = None
        type = None
        name = None

        if line is None:
            return None

        lineLen = len(line)
        if lineLen < 30 or lineLen > 250:
            # print("Line so long or short for parse, ignore.")
            return None

        res = cls.extractTimestampAndAction(line)

        if res is not None:
            [timestamp, actionPart] = res
        else:
            return None

        rawAction = None
        try:
            [name, rawAction] = actionPart.split(" ", 1)
        except ValueError:
            pass
        if rawAction is None:
            return None
        rawAction = rawAction.replace('"', '')

        # many shitty code for parsing actions
        if 'punched' in rawAction:
            action = 'punched'
            [name, other] = rawAction.split(' ', 1)
            typeAndNode = findStringBetween(rawAction, 'punched ', ' at ')
            if typeAndNode is None:
                type = 'player'
                node = findStringBetween(rawAction, 'player ', ' (')
            else:
                typeAndNode = typeAndNode.replace('"', '')
                [type, node] = typeAndNode.split(" ")
        elif 'right-clicks' in rawAction:
            action = 'right-clicks'
            typeAndNode = findStringBetween(rawAction, 'right-clicks ', ' at (')
            if typeAndNode is None:
                type = 'player'
                node = findStringBetween(rawAction, 'player ', ' (')
            elif 'object' in typeAndNode:
                type = 'LuaEntitySAO'
                node = findStringBetween(rawAction, 'LuaEntitySAO', ' at ')
            else:
                typeAndNode = typeAndNode.replace('"', '')
                [type, node] = typeAndNode.split(" ")
        elif 'activates' in rawAction:
            try:
                [action, node] = rawAction.split(' ')
            except Exception:
                # print('error ocurred while parsing activates log')
                # print(line)
                pass
        elif 'places node' in rawAction:
            action = 'places node'
            node = findStringBetween(rawAction, 'places node ', ' at ')
        elif 'digs' in rawAction:
            action = 'digs'
            node = findStringBetween(rawAction, 'digs ', ' at ')
        elif 'crafts' in rawAction:
            action = 'crafts'
            name = findStringBetween(rawAction, 'player ', ' crafts')
            typeAndNode = findStringBetween(rawAction, 'punched ', ' at ')
            if typeAndNode is None:
                type = 'player'
                node = findStringBetween(rawAction, 'player ', ' (')
            else:
                typeAndNode = typeAndNode.replace('"', '')
                [type, node] = typeAndNode.split(" ")
        elif ' uses ' in rawAction:
            node = findStringBetween(rawAction, 'uses', ',')
            pass
        else:
            try:
                # print(rawAction)
                if rawAction.count(' ') > 1:
                    [action, node, other] = rawAction.split(" ", 2)
                    if (action == 'takes' or action == 'moves') and "chest" in other:
                        pattern = r'takes\s+([^ ]+)' if action == 'takes' else r'moves\s+([^ ]+)'
                        match = re.search(pattern, rawAction)
                        if match:
                            node = match.group(1)
                            if action == 'moves':
                                count = findStringBetween(rawAction, node, 'to')
                                type = findStringBetween(rawAction, 'to ', " at")
                            else:
                                count = findStringBetween(rawAction, node, 'from')
                                type = findStringBetween(rawAction, 'from ', " at")

                            if count == ' ':
                                count = 1
                            elif count is not None:
                                count = count.strip()
                        else:
                            return None
                elif rawAction.count(' ') == 0:
                    pass
                elif rawAction.count(' ') == 1:
                    [rawAction, node] = rawAction.split(" ")
            except Exception:
                print('Unpack error')
                print(rawAction)

        coords = None
        if ' at ' in rawAction:
            rawCoords = rawAction.split(" at ", 1)[1]
            rawCoords = rawCoords.replace('"', '')
            rawCoords = rawCoords.replace("'", '')

            if rawCoords.count("(") > 1:
                coords = extractCoords(rawCoords.split(" ")[0])
            elif 'node under' in rawCoords:
                rawCoords = extractCoords(findStringBetween(rawCoords, 'node under=', 'above'))
            elif 'nothing' in rawCoords:
                coords = None
            elif findStringBetween(rawCoords, "(", ")") is not None:
                coords = findStringBetween("(", ")", rawCoords)
                if coords is not None:
                    coords = extractCoords(coords)
                else:
                    coords = None
            else:
                coords = None
            if coords is not None and len(coords) > 3:
                print("Error ocurred while parsing coordinates string")
                print(line)
        else:
            coords = None

        if node is not None:
            node = node.strip()

        return {
            "timestamp": timestamp,
            "name": name,
            "action": action,
            "meta_action": meta_action,
            "node": node,
            "count": count,
            "coords": coords,
            "type": type,
        }

    def logReaderGenerator(self):
        with open(self.logFilepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if len(line) == 0:
                    continue
                yield line

    @classmethod
    def extractTimestampAndAction(cls, targetStr):
        # length datetime string like 2023-10-27 14:47:35:
        if len(targetStr) < 21:
            return None

        splittedTimeAndOther = targetStr.split('#')
        if len(splittedTimeAndOther) != 2:
            return None

        [time, actionPart] = splittedTimeAndOther

        try:
            timestamp = timestamp = datetime.strptime(time, "%Y-%m-%d %H:%M:%S").timestamp()
        except Exception:
            print("Cant parse time from time string")
            print(f"Time string: {time}")
            return None
        del splittedTimeAndOther
        # [time, actionPart]
        timestamp = int(timestamp)
        return [timestamp, actionPart]

    @classmethod
    def cleanActionLogString(cls, line: str) -> str:
        return line.replace(f': {cls.actionPlaceholder}: ', '#')
