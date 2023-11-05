from src.minetest_log_parser.Parser.MinetestLogParser import MinetestLogParser

if __name__ == '__main__':
    input = "./test-data/debug.txt"
    minetestParser = MinetestLogParser(input, encoding='utf-8')
    act_dict = {}
    for parsedLog in minetestParser.read():
        print(parsedLog)
        pass

    # {'timestamp': 1699117200, 'name': 'Player7', 'action': 'places node', 'meta_action': None,
    # 'node': 'default:sandstonebrick', 'count': 1, 'coords': [138.0, 7.0, 632.0], 'type': None, 'logType': 'action'}
