import time
import random
import networkx as nx
from copy import deepcopy
from itertools import repeat
from matplotlib import pyplot
from collections import deque
from engine.players import Agent
from engine.data import getPaths, getDestinationCards, pointsByLength, colors

"""
TODO:
1. Longest route bonus is not given out at the end.
2. Right now it only simulates one game. Need it to simulate a batch of games and gather the data.
"""

class Game:

    def __init__(self, map: str, players: list[Agent], logs: bool, debug=False, drawGame=False) -> None:
        """
        The Ticket to Ride game engine in python.

        Map = a string representing the name of the map to play on (USA only)

        Players = a list of 2-4 players from engine.players to use for the game

        Logs = a boolean to enable printing of game logs

        Debug = a boolean to enable more descriptive game logs

        drawGame = a boolean to see a loose representation of the ending game map
        """
        self.debug = debug
        self.doLogs = logs
        self.mapName = map
        self.gameOver = False
        self.drawGame = drawGame
        self.logs = []
        self.board = nx.MultiGraph
        self.board_placed = nx.MultiGraph
        self.faceUpCards = list[str]
        self.trainCarDeck = deque[str]
        self.destinationCards = list[str]
        self.validGameMoves = [0, 1, 2, 3]
        self.destinationsDeck = deque[list[str]]
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
        self.endGame()
        if self.doLogs == True:
            self.log()
        if self.drawGame:
            pyplot.show()
    
    def build(self) -> None:
        """
        Builds a networkx MultiGraph representation of the map and the decks to be used as deques
        """

        # Build the board
        self.board = nx.MultiGraph()
        if len(self.players) == 4:
            self.board.add_edges_from((path[0], path[3], {'weight': int(path[1]), 'color': path[2], 'owner': ''}) for path in getPaths(self.mapName))
        else:
            self.board.add_edges_from((path[0], path[3], {'weight': int(path[1]), 'color': path[2], 'owner': ''}) for path in getPaths(self.mapName) if self.board.has_edge(path[0], path[3]) == False)
        
        # Build the train car deck
        traincar_deck = ['PINK']*12+['WHITE']*12+['BLUE']*12+['YELLOW']*12+['ORANGE']*12+['BLACK']*12+['RED']*12+['GREEN']*12+['WILD']*14
        random.shuffle(traincar_deck)
        self.trainCarDeck = deque(traincar_deck)

        # Deal the face up cards
        self.faceUpCards = [self.trainCarDeck.pop(), self.trainCarDeck.pop(), self.trainCarDeck.pop(), self.trainCarDeck.pop(), self.trainCarDeck.pop()]

        # Build the destination deck
        destination_deck = getDestinationCards(self.mapName)
        self.destinationCards = deepcopy(destination_deck)
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
        self.actionMap = { 0: list(self.board.edges.data(keys=True)), 1: self.faceUpCards, 2: self.trainCarDeck, 3: self.destinationCards }
    
    def placeTrains(self, player: Agent, actionDistribution: list[int], cardDistribution: list[str]) -> None:
        """
        Takes the distributions for placing trains and performs the move for the game. Uses the player object, actionDistribution, and cardDistribution.

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
            isTaken = False
            route = self.actionMap[0][action]
            if len(self.board.get_edge_data(route[0], route[1]).values()) > 1:
                for path in self.board.get_edge_data(route[0], route[1]).values():
                    if path['owner'] == '':
                        isTaken = False
                    elif path['owner'] == player.turnOrder:
                        isTaken = True
                        break
            else:
                if self.board.get_edge_data(route[0], route[1])[0]['owner'] != '':
                    isTaken = True

            # Debug Log
            if self.debug and isTaken:
                self.logs = self.logs + [f"    wanted {route} but taken.\n"]

            if isTaken:
                continue

            if route[3].get('weight') > player.trainsLeft:
                if self.debug:
                    self.logs = self.logs + [f"    wanted {route} but not enough trains.\n"]
                continue

            # see if player has the cards to place route
            # 1. Update the player train count and the player hand
            # 2. Update the game board
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
                            break
            else:
                if cardDistribution.index('WILD') < cardDistribution.index(route[3].get('color')):
                    if player.hand_trainCards.count(route[3].get('color')) >= route[3].get('weight'):
                        cards = list(repeat(route[3].get('color'), route[3].get('weight')))
                        canAfford = True
                    elif player.hand_trainCards.count('WILD') >= route[3].get('weight'):
                        cards = list(repeat('WILD', route[3].get('weight')))
                        canAfford = True
                else:
                    if player.hand_trainCards.count('WILD') >= route[3].get('weight'):
                        cards = list(repeat('WILD', route[3].get('weight')))
                        canAfford = True
                    elif player.hand_trainCards.count(route[3].get('color')) >= route[3].get('weight'):
                        cards = list(repeat(route[3].get('color'), route[3].get('weight')))
                        canAfford = True
            
            if self.debug and canAfford == False:
                self.logs = self.logs + [f"    wanted {route} but lacking cards.\n"]

            if canAfford:
                # print(f"   {self.board.get_edge_data(route[0], route[1]).values()}")
                if self.doLogs:
                    self.logs = self.logs + [f"   placed {route} using {cards}\n"]
                # 1. Update the player train count and the player hand
                player.points += pointsByLength[route[3].get('weight')]
                player.trainsLeft = player.trainsLeft - route[3].get('weight')
                for color in cards:
                    player.hand_trainCards.remove(color)
                # 2. Update the game board
                for path in self.board.get_edge_data(route[0], route[1]).values():
                    if path['owner'] == '':
                        path['owner'] = player.turnOrder
                        break
                # print(f"   {self.board.get_edge_data(route[0], route[1]).values()}")
                break
        
        if canAfford == False and self.validGameMoves == [0]:
            if self.doLogs:
                self.logs = self.logs + [f"   PLAYER {player.turnOrder} has no more valid moves. Game must end. {self.validGameMoves}\n"]
            self.gameOver = True
        if canAfford == False:
            return False
    
    def drawFaceUp(self, player: Agent, cardDistribution: list[str], requery) -> bool:
        """
        Takes the distributions for drawing from the face up cards and performs one draw of the face up card, updating the game to reflect it.

        Returns true if the player can make another move (did not pick up a wild), returns false if turn is over.

        TODO: clearing of face up cards in specific cirumstances has not been implemented yet. (ex. 3 wilds on the board clears the face up deck)
        """
        # 1. Find the next color to pick up
        # 2. Update player hand
        # 3. Update game board
        # 4. Ask for next card pick up given new game state unless a wild was picked up.
        isWild = bool
        for color in cardDistribution:
            isWild = True if color == "WILD" else False
            if isWild and requery:
                continue
            if color in self.faceUpCards:
                player.hand_trainCards.append(color)
                self.faceUpCards.remove(color)
                if 2 in self.validGameMoves and len(self.trainCarDeck) > 0:
                    self.faceUpCards.append(self.trainCarDeck.pop())
                    if len(self.trainCarDeck) == 0:
                        self.validGameMoves.remove(2)

                # Logging
                if self.doLogs:
                    self.logs = self.logs + [f"   picked up {color} from face up deck.\n"]

                break

        if isWild:
            return False
        else:
            return True

    def drawDestinationCards(self, player: Agent, actionDistribution: list[int], draw: list[list[str]]) -> None:
        """
        Performs the drawing of the destination cards given the distributions from the agent, updating the game to reflect the moves.

        Returns true if the player can make another move, returns false if turn is over.

        How it works: player is expected to make the first 3 indexes in actionDistribution as their top choices for cards. The game will take as many destinations available as are in the top 3. If none, it will take only one card - the first most desired one.
        """

        if self.doLogs:
            self.logs = self.logs + [f"   picked up destination cards: {draw}\n"]

        taking = []
        found = None

        for wantedCard in actionDistribution[:3]:
            for index, destinationCard in enumerate(draw):
                if destinationCard == self.destinationCards[wantedCard]:
                    found = True
                    taking.append(index)
                    break

        if found == None:
            for wantedCard in actionDistribution[3:]:
                for index, destinationCard in enumerate(draw):
                    if destinationCard == self.destinationCards[wantedCard]:
                        found = True
                        taking.append(index)
                        break
                if found:
                    break
        
        for x in range(3):
            if x not in taking:
                self.destinationsDeck.appendleft(draw[x])
            else:
                player.hand_destinationCards.append(draw[x])
                player.points -= int(draw[x][1])
                # Logging
                if self.doLogs:
                    self.logs = self.logs + [f"   taking {draw[x]}\n"]

    def performAction(self, player: Agent, requery=False, i=None):
        """
        Does complete handling of all actions:

        * Will do valid action checks

        * Will re-query the agent on follow up decisions

        * Responsible for updating the game state after each player's turn
        """
        if i == []:
            self.gameOver = True
            return

        # If not asking for specific move
        if i == None:
            action, actionDistribution, cardDistribution = player.turn(self.board, self.faceUpCards, [agent.points for agent in self.players], [len(agent.hand_trainCards) for agent in self.players], [len(agent.hand_destinationCards) for agent in self.players], self.actionMap)
            while action not in self.validGameMoves:
                action, actionDistribution, cardDistribution = player.turn(self.board, self.faceUpCards, [agent.points for agent in self.players], [len(agent.hand_trainCards) for agent in self.players], [len(agent.hand_destinationCards) for agent in self.players], self.actionMap)
        # If asking for specific move
        else:
            if i[0] == 3:
                draw = [self.destinationsDeck.pop(), self.destinationsDeck.pop(), self.destinationsDeck.pop()]
                if len(self.destinationsDeck) < 3:
                    self.validGameMoves.remove(3)
                action, actionDistribution, cardDistribution = player.turn(self.board, self.faceUpCards, [agent.points for agent in self.players], [len(agent.hand_trainCards) for agent in self.players], [len(agent.hand_destinationCards) for agent in self.players], self.actionMap, i, destCardDeal=draw)
                self.drawDestinationCards(player, actionDistribution, draw)
            else:
                action, actionDistribution, cardDistribution = player.turn(self.board, self.faceUpCards, [agent.points for agent in self.players], [len(agent.hand_trainCards) for agent in self.players], [len(agent.hand_destinationCards) for agent in self.players], self.actionMap, i)           
    
        # Agent wants to place trains
        if action == 0:
            store = self.placeTrains(player, actionDistribution, cardDistribution)
            if store == False:
                valid = deepcopy(self.validGameMoves)
                valid.remove(0)
                self.performAction(player, False, valid)
        # Agent wants to draw from the face up pile
        elif action == 1:
            anotherMove = self.drawFaceUp(player, cardDistribution, requery)
            if anotherMove and requery == False:
                # Requery the agent with valid moves 1 and 2 available - drawing from face up or down cards.
                x = []
                if 1 in self.validGameMoves:
                    x.append(1)
                if 2 in self.validGameMoves:
                    x.append(2)
                self.performAction(player, requery=True, i=x)
        # Agent wants to draw from the face down pile
        elif action == 2:
            color = self.trainCarDeck.pop()
            player.hand_trainCards.append(color)
            # Recheck for validity
            if len(self.trainCarDeck) == 0:
                self.validGameMoves.remove(2)
            # Logging
            if self.doLogs:
                self.logs = self.logs + [f"   picked up {color} from face down deck.\n"]
            if requery == False:
                x = []
                if 1 in self.validGameMoves:
                    x.append(1)
                if 2 in self.validGameMoves:
                    x.append(2)
                self.performAction(player, requery=True, i=x)
        # Agent wants to draw new destination cards
        elif action == 3 and requery == False:
            self.performAction(player, i=[3], requery=True)
            
    def play(self):
        """
        Plays the whole game out once.
        """
        lastTurn = None
        endedGame = None
        while self.gameOver == False:
            for player in self.players:

                # Do global move validity checks and update the valid moves
                if len(self.destinationsDeck) < 3 and 3 in self.validGameMoves:
                    self.validGameMoves.remove(3)
                if len(self.trainCarDeck) == 0 and 2 in self.validGameMoves:
                    self.validGameMoves.remove(2)
                if len(self.faceUpCards) == 0 and 1 in self.validGameMoves:
                    self.validGameMoves.remove(1)

                # Logging
                if self.doLogs:
                    if self.debug:
                        addLogs = [f"\nTURN {self.turn}\n", f"CARDS UP {self.faceUpCards}\n", f"CARDS DOWN {self.trainCarDeck}\n", f"DEST DECK {self.destinationsDeck}\n", f" PLAYER {player.turnOrder} {player.hand_trainCards}, destinations {player.hand_destinationCards}, trains {player.trainsLeft}, points {player.points}\n"] 
                    else:
                        addLogs = [f"\nTURN {self.turn}\n", f"CARDS UP {self.faceUpCards}\n", f" PLAYER {player.turnOrder} {player.hand_trainCards}, destinations {player.hand_destinationCards}, trains {player.trainsLeft}, points {player.points}\n"]
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
                        else:
                            player.points -= int(destinationCard_deal[i][1])

                    self.turn += 1
                    
                else:
                    if self.validGameMoves != []:
                        self.performAction(player)
                    else:
                        self.gameOver = True
                        break
                    if player.trainsLeft < 3:
                        lastTurn = True
                        self.gameOver = True
                        endedGame = player.turnOrder
                        if self.doLogs:
                            self.logs = self.logs + [f"\nPLAYER {player.turnOrder} INITIATES LAST ROUND\n"]
                        break

                    self.turn += 1
                
                if self.gameOver == True:
                    break

        if lastTurn == True:
            if endedGame == len(self.players) - 1:
                playerOrder = [z for z in range(len(self.players))]
            elif endedGame == 0:
                playerOrder = [z for z in range(1, len(self.players))] + [0]
            else:
                playerOrder = [z for z in range(endedGame, len(self.players))] + [x for x in range(0, endedGame)]

            for playerIndex in playerOrder:
                self.turn += 1
                if self.doLogs:
                    if self.debug:
                        addLogs = [f"\nTURN {self.turn}\n", f"CARDS UP {self.faceUpCards}\n", f"CARDS DOWN {self.trainCarDeck}", f" PLAYER {self.players[playerIndex].turnOrder} {self.players[playerIndex].hand_trainCards}, destinations {self.players[playerIndex].hand_destinationCards}, trains {self.players[playerIndex].trainsLeft}, points {self.players[playerIndex].points}\n"]
                    else:
                        addLogs = [f"\nTURN {self.turn}\n", f"CARDS UP {self.faceUpCards}\n", f" PLAYER {self.players[playerIndex].turnOrder} {self.players[playerIndex].hand_trainCards}, destinations {self.players[playerIndex].hand_destinationCards}, trains {self.players[playerIndex].trainsLeft}, points {self.players[playerIndex].points}\n"]
                    self.logs = self.logs + addLogs
                self.performAction(self.players[playerIndex])

    def endGame(self):
        """
        Called after one/all game(s) have been finished.
        """

        # Route completion testing
        # 1. Draw a new graph with only the destination cards for that player
        # 2. Check that graph and tally the points
        # 3. Do that for all players
        if self.drawGame:
            pos = nx.spectral_layout(self.board) 
            nx.draw_networkx_nodes(self.board, pos)
            nx.draw_networkx_labels(self.board, pos, font_size=6)
        for player in self.players:
            edges = [edge for edge in self.board.edges(data=True) if edge[2]['owner'] == player.turnOrder]
            boardPlaced = nx.MultiGraph(edges)
            for route in player.hand_destinationCards:
                try:
                    completed = nx.has_path(boardPlaced, route[0], route[2])
                except:
                    completed = False
                if completed:
                    player.points += int(route[1])
                    if self.doLogs:
                        self.logs = self.logs + [f"PLAYER {player.turnOrder} awarded {route[1]} points for completing {route}\n"]
            if self.drawGame:     
                nx.draw_networkx_edges(self.board, pos, edges, edge_color=colors[player.turnOrder], connectionstyle=f"arc3, rad = 0.{player.turnOrder}", arrows=True)
                player.color = colors[player.turnOrder]
        
        if self.drawGame:
            for player in self.players:
                if self.drawGame:
                    print(f"PLAYER {player.turnOrder + 1} ({player.name}): {player.points} [{player.color}]")
                else:
                    print(f"PLAYER {player.turnOrder + 1} ({player.name}): {player.points}")

    def log(self):
        logs = open("log.txt", "w")
        logs.writelines(self.logs)

class Simulate:

    def __init__(self, map: str, players: list[Agent], logs: bool, debug: bool, runs: int, drawGame: bool) -> None:

        iterations = runs

        if runs == 1:
            Game(map, players, logs, debug, drawGame)

        else:
            
            start = time.time()

            playerInfo = { player.name: 0 for player in players }
            print(f"Simulating {runs} games...")

            while runs != 0:

                for player in players:
                    player = player.__init__(player.name)

                game = Game(map, players, logs, debug, False)

                for player in players:
                    playerInfo[player.name] += player.points

                runs -= 1
            
            for name, points in playerInfo.items():
                print(f"{name} {points/iterations} avg points")
            
            end = time.time()
            print(f"Completed in {round(end-start, 2)} seconds")