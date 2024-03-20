from random import sample, randint, shuffle
import engine
import networkx as nx
from networkx import MultiGraph
from engine.data import listColors

class Agent:
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand_trainCards = []
        self.hand_destinationCards = []
        self.trainsLeft = 45
        self.points = 0
        self.color = str
        self.turnOrder = int

    def firstTurn(self, deal: list[list[str]]) -> list[int]:
        """
        The method for selecting the initial destination cards on the first turn of the game, returns a list of integers as info for the game object to sync with the player objects
        """
        pass

    def turn(self, board: nx.MultiGraph, faceUpCards: list[str], playerPoints: list[int], playerHandSizes: list[int], playerDestSizes: list[int], actionMap: dict[int, list], i = None, destCardDeal = None) -> tuple[int, list[int], list[str]]:
        """
        Returns a number corresponding to the desired turn action to make given the template board, the current board, the face up cards, the points of each player, the size of each players hand, how many destination cards the other players have, and the action map. Optionally, use i to request a action desire (ex. for a card draw you must draw 2 cards, this would be done by requesting the next card draw to fulfill the second draw requirement)
        
        Returns a tuple of (turn action, action desire, card desire), where action desire is an iterable sequence of indexes corresponding to the actionMap that will be checked left to right for valid moves. NOTE: the action distribution is only relevant for drawing destination cards and placing trains.
        
        Card desires is an iterable sequence of card color strings that represents the need for each color of card [highest, ..., lowest], lowest need means you no longer need this card and should be considered first in placing.

        Turn action indexes:
        0 - Place Trains
        1 - Draw (Face Up)
        2 - Draw (Face Down)
        3 - Draw (Destination Cards)

        action desires depend on the map, but generally will be an iterable describing specifics of the chosen action
        """

class Random(Agent):
    def __init__(self, name="Random") -> None:
        """
        Completely random agent for Ticket to Ride.
        """
        Agent.__init__(self, name)

    def firstTurn(self, deal: list[list[str]]) -> list[int]:
        selections = sample([0, 1, 2], randint(2, 3))
        for cardNum in selections:
            self.hand_destinationCards.append(deal[cardNum])
        return selections
    
    def turn(self, board: MultiGraph, faceUpCards: list[str], playerPoints: list[int], playerHandSizes: list[int], playerDestSizes: list[int], actionMap: dict[int, list], i = None, destCardDeal = None) -> tuple[int, list[int], list[str]]:
        if i == None:
            i = randint(0, 3)
        else:
            shuffle(i)
            i = i[0]
        actionDistribution = [x for x in range(0, len(actionMap[i]), 1)]
        shuffle(actionDistribution)
        cardsDistribution = listColors()
        shuffle(cardsDistribution)
        move = (i, actionDistribution, cardsDistribution)
        return move


class Human(Agent):
    def __init__(self) -> None:
        Agent.__init__(self, "Human")
    
    def firstTurn(self, deal: list[list[str]]) -> list[int]:
        pass