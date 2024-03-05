import random
import networkx as nx
from itertools import repeat
from collections import deque
from matplotlib import pyplot
from players import Random, Human, Agent
from data import getPaths, getDestinationCards

class Game:

    def __init__(self, map: str, players: list[Agent], logs: bool, debug=False) -> None:
        """
        Creates a Map object given the official name of the map, a list of players, and a log option, debug adds more details to the log and is false by default
        """
        self.debug = debug
        self.doLogs = logs
        self.logs = list[str]
        self.mapName = map
        self.board = nx.MultiGraph
        self.currentBoard = nx.MultiGraph
        self.trainCarDeck = deque[str]
        self.faceUpCards = list[str]
        self.destinationsDeck = deque[list[str]]
        self.gameOver = False
        self.players = players if ((2 <= len(players) <= 4)) else None
        if self.players == None:
            raise ValueError("There must be between 2-4 players.")
        random.shuffle(self.players)
        self.turn = 1 - len(players)
        self.build()
        self.init()
        self.play()
        if self.doLogs == True:
            self.log()
    
    def build(self) -> None:
        """
        Builds a networkx MultiGraph representation of the map and the decks to be used as queues
        Note: The queue implementation requires that you appendleft() if adding and pop() if drawing a card
        """

        board = nx.MultiGraph()
        paths = getPaths(self.mapName)
        for path in paths:
            board.add_edge(path[0], path[3], weight=int(path[1]), color=path[2], owner="")
        self.board = board

        curGame = nx.MultiGraph()
        nodes = list(board.nodes())
        for node in nodes:
            curGame.add_node(node)

        # nx.draw_networkx(curGame, pos=nx.spring_layout(curGame))
        # pyplot.show()
            
        traincar_deck = list(repeat("PINK", 12)) + list(repeat("WHITE", 12)) + list(repeat("BLUE", 12)) + list(repeat("YELLOW", 12)) + list(repeat("ORANGE", 12)) + list(repeat("BLACK", 12)) + list(repeat("RED", 12)) + list(repeat("GREEN", 12)) + list(repeat("WILD", 14))
        random.shuffle(traincar_deck)
        traincar_deck = deque(traincar_deck)
        self.trainCarDeck = traincar_deck

        self.faceUpCards = [self.trainCarDeck.pop(), self.trainCarDeck.pop(), self.trainCarDeck.pop(), self.trainCarDeck.pop(), self.trainCarDeck.pop()]

        destination_deck = getDestinationCards(self.mapName)
        random.shuffle(destination_deck)
        destination_deck = deque(destination_deck)
        self.destinationsDeck = destination_deck
    
    def init(self):
        """
        Initializes the game board and players for playing to begin.
        """
        if self.doLogs == True:
            logStr = ""
        for i, player in enumerate(self.players):
            for _ in range(4):
                player.hand_trainCards.append(self.trainCarDeck.pop())
                
            player.turnOrder = i + 1

            if self.doLogs == True:
                logStr = logStr + f"{player.turnOrder}. {player.name}\n"
            # print(player.name, player.turnOrder, player.hand_trainCards)
        
        if self.doLogs == True:
            self.logs = ["TICKET TO RIDE\n", logStr, "--------------------\n"]

    def play(self):
        """
        Plays the whole game out once.
        """
        while self.gameOver == False:
            for player in self.players:

                # Logging
                if self.doLogs == True:
                    addLogs = [f"\nTURN {self.turn}\n", f"CARDS UP {self.faceUpCards}\n", f" PLAYER {player.turnOrder} {player.hand_trainCards}, destinations {player.hand_destinationCards}, trains {player.trainsLeft}\n"]
                    self.logs = self.logs + addLogs

                # Starting the game
                if self.turn < 1:

                    destinationCard_deal = [self.destinationsDeck.pop(), self.destinationsDeck.pop(), self.destinationsDeck.pop()]
                    taken = player.firstTurn(destinationCard_deal)

                    # Logging
                    if self.doLogs == True:
                        addLogs = [f"   dealt {destinationCard_deal}\n", f"   keeps {player.hand_destinationCards}\n"]
                        self.logs = self.logs + addLogs
                        if self.debug == True:
                            self.logs = self.logs + [f" PLAYER {player.turnOrder} {player.hand_trainCards}, destinations {player.hand_destinationCards}, trains {player.trainsLeft}\n"]

                    # Sync game object destinations deck with player objects (put the unchosen cards back into the deck)
                    for i in range(3):
                        if i not in taken:
                            self.destinationsDeck.appendleft(destinationCard_deal[i])

                    self.turn += 1
                    
                else:
                    
                    validStates = player.turn(self.board, self.currentBoard, self.faceUpCards)
                    print(validStates)

                    self.gameOver = True
                    self.turn += 1

    def log(self):
        logs = open("log.txt", "w")
        logs.writelines(self.logs)

agents = [Random(), Random()]
Game("USA", agents, True, debug=False)