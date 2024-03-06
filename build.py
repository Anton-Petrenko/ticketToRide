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
        self.trainCarDeck = deque[str]
        self.faceUpCards = list[str]
        self.destinationsDeck = deque[list[str]]
        self.gameOver = False
        self.players = players if ((2 <= len(players) <= 4)) else None
        if self.players == None:
            raise ValueError("There must be between 2-4 players.")
        random.shuffle(self.players)
        self.turn = 1 - len(players)
        self.actionMap = dict[int, list]
        self.build()
        self.init()
        self.getActionMap()
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
                
            player.turnOrder = i

            if self.doLogs == True:
                logStr = logStr + f"{player.turnOrder}. {player.name}\n"
            # print(player.name, player.turnOrder, player.hand_trainCards)
        
        if self.doLogs == True:
            self.logs = ["TICKET TO RIDE\n", logStr, "--------------------\n"]
    
    def getActionMap(self):
        """
        Returns the action map of the current game. The action map maps integers to the specific actions for that action. For example, an agent may choose to place a train route but must know all possibilities available to it - which depends on the map. Thus, this function is called per game object as it will be specific to each game/map. Can also be viewed as a "valid actions" tracker.

        Turn action indexes:
        0 - Place Trains (0, list[tuple])
        1 - Draw (Face Up) (1, list[str])
        2 - Draw (Face Down) (2, deque[str])
        3 - Draw (Destination Cards) (3, deque[list[str]])
        """
        self.actionMap = { 0: list(self.board.edges.data(keys=True)), 1: self.faceUpCards, 2: self.trainCarDeck, 3: self.destinationsDeck }

    def performAction(self, player: Agent):
        """
        Does complete handling of all actions:

        * Will do valid action checks

        * Will re-query the agent on follow up decisions

        * Responsible for updating the game state after each player's turn
        """
        action, specific = player.turn(self.board, self.faceUpCards, [agent.points for agent in self.players], [len(agent.hand_trainCards) for agent in self.players], [len(agent.hand_destinationCards) for agent in self.players], self.actionMap)

        # Agent wants to place trains
        if action == 0:
            
            routeToPlace = self.actionMap[action][specific]
            routeMetadata = routeToPlace[3]
            print(f"Wants to place ")
            print(locals()['routeMetadata']['owner'])
            # Availability check
            

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

                # Starting the game (deal out initial destination cards)
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

                    # Update the action map
                    self.getActionMap()

                    self.turn += 1
                    
                else:
                    
                    self.performAction(player)

                    self.gameOver = True
                    self.turn += 1

    def log(self):
        logs = open("log.txt", "w")
        logs.writelines(self.logs)

agents = [Random(), Random()]
Game("USA", agents, True, debug=False)