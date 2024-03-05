from random import sample, randint
import networkx as nx
from networkx import MultiGraph

class Agent:
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand_trainCards = []
        self.hand_destinationCards = []
        self.trainsLeft = 45
        self.points = 0
        self.turnOrder = int

    def firstTurn(self, deal: list[list[str]]) -> list[int]:
        """
        The method for selecting the initial destination cards on the first turn of the game, returns a list of integers as info for the game object to sync with the player objects
        """
        pass

    def validMoves(self, board: nx.MultiGraph, currentBoard: nx.MultiGraph, faceUpCards: list[str]) -> list[int]:
        """
        Returns a list of moves that are valid given the board, current board, and face up cards
        """
        return [1, 2]


    def turn(self, board: nx.MultiGraph, currentBoard: nx.MultiGraph, faceUpCards: list[str]) -> int:
        """
        Given the board (for info), the current game board, and the cards showing face up, return a move to make (int)
        """

class Random(Agent):
    def __init__(self) -> None:
        Agent.__init__(self, "Random")

    def firstTurn(self, deal: list[list[str]]) -> list[int]:
        selections = sample([0, 1, 2], randint(2, 3))
        for cardNum in selections:
            self.hand_destinationCards.append(deal[cardNum])
        return selections
    
    def turn(self, board: nx.MultiGraph, currentBoard: nx.MultiGraph, faceUpCards: list[str]) -> int:
        return self.validMoves(board, currentBoard, faceUpCards)

class Human(Agent):
    def __init__(self) -> None:
        Agent.__init__(self, "Human")
    
    def firstTurn(self, deal: list[list[str]]) -> list[int]:
        for i, card in enumerate(deal):
            print(f"{i}. {card}")

        choice = int
        choices = []

        while True:
            choice = input("Enter first destination card choice: ")
            try:
                if 0 <= int(choice) < len(deal):
                    choices.append(int(choice))
                    break
            except:
                pass
        
        while True:
            choice2 = input("Enter second destination card choice: ")
            try:
                if 0 <= int(choice2) < len(deal) and choice2 != choice:
                    choices.append(int(choice2))
                    break
            except:
                pass
