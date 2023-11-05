# replaces arrays of substrings in string to target substring
def raplaceSubstringsTo(targetStr, substringArr, replacement=''):
    for substr in substringArr:
        targetStr = targetStr.replace(substr, replacement)
    return targetStr


# like split, but works from end of string
def splitByRightSide(targetStr, delimiter):
    index = targetStr.rfind(delimiter)

    if index != -1:
        firstPart = targetStr[:index]
        secondPart = targetStr[index + len(delimiter):]
        return [firstPart, secondPart]
    else:
        return None


# extract float coords from string (x,y,z, ..., k, m) format and return list of floats
def extractCoords(coordsString):
    coordsList = raplaceSubstringsTo(coordsString, ["(", ")"], '').split(',')

    for idx, coord in enumerate(coordsList):
        coord = coord.strip()
        if coord == '':
            return None
        coordsList[idx] = float(coord)

    return coordsList


# finding string between two substrings
def findStringBetween(input_string, start_string, end_string):
    start_index = input_string.find(start_string)
    if start_index == -1:
        return None

    end_index = input_string.find(end_string, start_index + len(start_string))
    if end_index == -1:
        return None

    return input_string[start_index + len(start_string):end_index]
