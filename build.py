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
    
    def init(self) -> None:
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
    
    def getActionMap(self) -> None:
        """
        Returns the action map of the current game. The action map maps integers to the specific actions for that action. For example, an agent may choose to place a train route but must know all possibilities available to it - which depends on the map. Thus, this function is called per game object as it will be specific to each game/map. 

        NOTE: This does not update per move, it simply provides indexes for each possible action in a game for the agents to use.

        Turn action indexes:
        0 - Place Trains (0, list[tuple])
        1 - Draw (Face Up) (1, list[str])
        2 - Draw (Face Down) (2, deque[str])
        3 - Draw (Destination Cards) (3, deque[list[str]])
        """
        self.actionMap = { 0: list(self.board.edges.data(keys=True)), 1: self.faceUpCards, 2: self.trainCarDeck, 3: self.destinationsDeck }
    
    def cardsForPlacing(self, player: Agent, actionDistribution: list[int], cardDistribution: list[str]) -> tuple[list[str], tuple]:
        """
        Takes the distributions for placing trains and turns it into a readable move for the game. Uses the player object, actionDistribution, and cardDistribution.

        NOTE: It will check all possible colors first, if nothing works, it will then check (from least to most desired) if wilds can fill up the rest.

        Outputs the cards to use in a list (from the agent) and the route as the given tuple from networkx
        """
        # 1. See if the player can afford that action
        # 2. See if the edge is taken
        # 3. If both true, return
        canAfford = False
        isTaken = False
        cards = list[str]
        route = None

        for action in actionDistribution:
            route = self.actionMap[0][action]
            isTaken = True if route[3].get('owner') != '' else False # see if route is taken

            # Debug Log
            if self.debug and isTaken:
                self.logs = self.logs + [f"    wanted {route} but taken."]

            if isTaken:
                continue

            print(route)
            print(f"Player cards: {player.hand_trainCards}")

            # see if player has the cards to place route
            if route[3].get('color') == 'GRAY':
                
                playerWildNum = player.hand_trainCards.count('WILD')
                wildFound = False

                for color in reversed(cardDistribution):

                    if wildFound == False and color == 'WILD':
                        wildFound = True
                        continue
                    playerColorNum = player.hand_trainCards.count(color)

                    if wildFound:
                        if playerWildNum >= route[3].get('weight'):
                            cards = list(repeat('WILD', route[3].get('weight')))
                            canAfford = True
                            break
                        elif playerWildNum + playerColorNum == route[3].get('weight'):
                            cards = list(repeat('WILD', playerWildNum)) + list(repeat(color, playerColorNum))
                            canAfford = True
                            break
                        elif playerWildNum + playerColorNum > route[3].get('weight'):
                            playerColorNum = route[3].get('weight') - playerWildNum
                            cards = list(repeat('WILD', playerWildNum)) + list(repeat(color, playerColorNum))
                            canAfford = True
                            break
                    else:
                        if playerColorNum >= route[3].get('weight'):
                            cards = list(repeat(color, route[3].get('weight')))
                            canAfford = True
                            print("4")
                            break
            elif player.hand_trainCards.count(route[3].get('color')) >= route[3].get('weight'):
                cards = list(repeat(player.hand_trainCards.count(route[3].get('color')), route[3].get('weight')))
                canAfford = True
            
            if self.debug and canAfford == False:
                self.logs = self.logs + [f"    wanted {route} but lacking cards."]

            if canAfford == False:
                print(f"wanted {route} but lacking cards.")

            if canAfford:
                break
        

    def placeTrains(self, player: Agent, useCards: list[str], route: tuple) -> None:
        """
        Places trains for the given player. Uses the player object, the cards it wants to use ['BLUE', 'BLUE', 'WILD'] and the edge tuple directly from Multigraph that contains the keys at index 3.
        """
        
    
    def performAction(self, player: Agent):
        """
        Does complete handling of all actions:

        * Will do valid action checks

        * Will re-query the agent on follow up decisions

        * Responsible for updating the game state after each player's turn
        """
        action, actionDistribution, cardDistribution = player.turn(self.board, self.faceUpCards, [agent.points for agent in self.players], [len(agent.hand_trainCards) for agent in self.players], [len(agent.hand_destinationCards) for agent in self.players], self.actionMap)

        # Agent wants to place trains
        if action == 0:
            cards, route = self.cardsForPlacing(player, actionDistribution, cardDistribution)
            self.placeTrains(player, cards, route)

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