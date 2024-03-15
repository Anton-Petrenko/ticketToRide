import re

pointsByLength = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}
colors = {0: 'red', 1: 'blue', 2: 'orange', 3: 'purple'}

def getPaths(map: str) -> list[list[str]]:
    """
    Takes a map name and returns a list of paths between cities where each item is an array [city1, length, color, city2] as strings
    """
    lines = open(f"{map}_paths.txt").readlines()
    paths = []
    for path in lines:
        data = re.search('(^\D+)(\d)\W+(\w+)\W+(.+)', path)
        paths.append([data.group(1).strip(), data.group(2).strip(), data.group(3).strip(), data.group(4).strip()])

    return paths

def getDestinationCards(map: str) -> list[list[str]]:
    """
    Takes a map name and returns a list of paths between cities where each item is an array [city1, points, city2] as strings
    """
    lines = open(f"{map}_destinations.txt").readlines()
    cards = []
    for card in lines:
        data = re.search('(^\D+)(\d+)\s(.+)', card)
        cards.append([data.group(1).strip(), data.group(2).strip(), data.group(3).strip()])
    
    return cards

def listColors() -> list[str]:
    return ['PINK', 'WHITE', 'BLUE', 'YELLOW', 'ORANGE', 'BLACK', 'RED', 'GREEN', 'WILD']