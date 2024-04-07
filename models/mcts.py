import math
from engine.build import State, Action, Game
from engine.data import listColors, listDestTakes
from models.network import Network
from copy import deepcopy

class Node:
    """
    The nodes in the MCTS tree
    
    Game state - of custom type State (build.py)
    """
    def __init__(self, state: State, priorProb=None, parent=None) -> None:
        self.state = state
        self.visitCount = 0             # N(s,a)
        self.priorProb = priorProb      # P(s,a)
        self.aggregateWinningProb = 0   # W(s,a)
        self.parent = parent
        """The parent of the node - of type Node"""
        self.children: list[Node] = []          
        """The children of the node - of type [ Node, Node, ... ]"""
        self.fromAction: Action = []
        """Each node that is a child stores the action (from its parent) that led to it - of custom type Action"""

    def getMeanWinningProb(self) -> float:
        """Return Q(s,a) - the mean winning probaility for a node/state"""
        if self.visitCount == 0:
            return float(0)
        return float(self.aggregateWinningProb / self.visitCount)
    
    def isExpandedNode(self) -> bool:
        return len(self.children) > 0

class MonteCarloSearch:
    """The Monte Carlo class for the Ticket to Ride Engine, using a state, it executes the desired number of simulations on that state"""

    def __init__(self, root: Node, simulations=1, pb_c_base=19652, pb_c_init=1.25) -> None:
        self.root: Node = root
        self.network: Network = Network(root.state.map)
        self.simulations = simulations
        self.pb_c_base = pb_c_base
        self.pb_c_init = pb_c_init
        self.search()

    def getValidMoves(self, state: State, previousAction=None, pickedUpWildFromFaceUp=False) -> list[Action]:
        """Returns a list of type Action that are possible to take from a given state of type State
        
        previousAction - context parameter for use in actions that change the game state but not whose turn it is (drawing face up card)"""

        nextPlayer = state.currentPlayer
        actionList: list[Action] = []

        # Check for 0 - Placing trains
        for route in state.board.edges(data=True):

            weight = route[2]['weight']
            # Criteria for ineligible:
            # 1. Taken
            # 2. Not enough cards
            if route[2]['owner'] != '':
                continue

            # Can this be completed at all (either color or color + wilds)?
            # If it can, every combination of cards must be returned. Caveat: all of one color must be used - the engine is not set up for splitting hands. For example, if a player holds 4 blues and 2 wilds and the route calls for 3 blues. There are two combinations possible - 3BLUE and 2WILD, 1BLUE. The engine will never perform a 2BLUE, 1WILD due to the nature of the "desire" architecture for denoting moves.

            # If the route is a color (not gray)
            if route[2]['color'] != 'GRAY':

                routeColor = route[2]['color']
                numColor = nextPlayer.hand_trainCards.count(routeColor)
                numWilds = nextPlayer.hand_trainCards.count('WILD')

                if numColor == 0:
                    continue
                elif numColor < weight:
                    # Less than needed - see if wilds can fill it up
                    if numWilds > 0:
                        if numWilds + numColor == weight:
                            actionList.append(Action(0, route, [routeColor, 'WILD']))
                        elif numWilds + numColor > weight:
                            actionList.append(Action(0, route, [routeColor, 'WILD']))
                            if numWilds < weight:
                                actionList.append(Action(0, route, ['WILD', routeColor]))
                elif numColor >= weight:
                    actionList.append(Action(0, route, [routeColor]))
                    if 0 < numWilds < weight:
                        actionList.append(Action(0, route, ['WILD', routeColor]))
            
            # If the route is gray
            else:
                numWilds = nextPlayer.hand_trainCards.count('WILD')
                for color in listColors():
                    # Check if it can be completed with just that color (doesn not include WILD)
                    numColor = nextPlayer.hand_trainCards.count(color)
                    if numColor == 0 or color == 'WILD':
                        # None of color
                        continue
                    elif numColor < weight:
                        # Less than needed - see if wilds can fill it up
                        if numWilds > 0:
                            if numWilds + numColor == weight:
                                actionList.append(Action(0, route, [color, 'WILD']))
                            elif numWilds + numColor > weight:
                                actionList.append(Action(0, route, [color, 'WILD']))
                                if numWilds < weight:
                                    actionList.append(Action(0, route, ['WILD', color]))
                    elif numColor >= weight:
                        # More than needed or equal
                        actionList.append(Action(0, route, [color]))
                        # Wildcard cases
                        if numWilds < weight and numWilds > 0:
                            actionList.append(Action(0, route, ['WILD', color]))
                if numWilds >= weight:
                    actionList.append(Action(0, route, ['WILD'])) 
        
        # Check for 1 & 2 - Draw Face Up or from Deck
        if previousAction == 1:
            # If we are drawing the second card
            if pickedUpWildFromFaceUp == False:
                # and the first one was not a wild
                for color in state.faceUpCards:
                    actionList.append(Action(1, colorPicked=[color]))
                if len(state.trainCarDeck) >= 1:
                    actionList.append(Action(2))
        elif previousAction == None:
            if len(state.faceUpCards) + len(state.trainCarDeck) >= 2:
                for color in state.faceUpCards:
                    actionList.append(Action(1, colorPicked=[color]))
                if len(state.trainCarDeck) >= 1:
                    actionList.append(Action(2))
        
        # Check for 3 - Draw Destination Cards
        if previousAction == 3:
            for take in listDestTakes():
                actionList.append(Action(3, destinationsPicked=take))
        elif previousAction == None:
            actionList.append(Action(3))

        # debug output of valid moves
        # i = 0
        # for action in actionList:
        #     i += 1
        #     if action.action == 0:
        #         print(action.action, action.routeToPlace, action.colorsUsed)
        #     elif action.action == 1:
        #         print(action.action, action.colorPicked)
        #     elif action.action == 2:
        #         print(action.action)
        #     elif action.action == 3:
        #         print(action.action, action.destinationsPicked)
        # print(f"Possible moves from turn {state.turn} = {i}")

    def ucb_score(self, parent: Node, child: Node) -> float:
        pb_c = math.log((parent.visitCount + self.pb_c_base + 1) / self.pb_c_base) + self.pb_c_init
        pb_c *= math.sqrt(parent.visitCount) / (child.visitCount + 1)
        U_sa = pb_c * child.priorProb
        Q_sa = child.getMeanWinningProb()
        return U_sa + Q_sa

    def select_child(self, node: Node) -> Node:
        """Selects the child based on the CPUCT formula in the AlphaGoZero paper"""
        score, action, child = max((self.ucb_score(node, child), child.fromAction, child) for child in node.children)
        return child
    
    def evaluateNode(self, node: Node, network: Network) -> int:
        return network.play(node.state) 

    def backprop(self):
        pass

    def search(self):

        a, Dc, Dd, Dr, w = self.evaluateNode(self.root, self.network)
        quit()

        for _ in range(self.simulations):
            currentNode = self.root # Start at the beginning
            searchPath: list[Node] = [] # The actions that have brought us to this state in MCTS
            while currentNode.isExpandedNode(): # If a node has children
                node = self.select_child(currentNode) # Select one
                searchPath.append(node)
    
