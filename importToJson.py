from src.Parser.MinetestLogParser import MinetestLogParser

if __name__ == '__main__':
    input = "./debug.txt"
    output = "./debugJson.txt"
    minetestParser = MinetestLogParser(input)

    minetestParser.importToJson(output)
