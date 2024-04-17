import math

import numpy
from engine.build import State, Action, Game, Agent
from engine.data import listColors, listDestTakes, product, indexByColor
from models.network import Network
from copy import deepcopy

class Node:
    """
    The nodes in the MCTS tree
    
    Game state - of custom type State (build.py)
    """
    def __init__(self, state: State, priorProb=None, parent=None, fromAction=None, color=None, destDeal=None) -> None:
        self.state = state
        self.visitCount = 1             # N(s,a)
        self.priorProb = priorProb      # P(s,a)
        self.aggregateWinningProb = 0   # W(s,a)
        self.parent = parent
        """The parent of the node - of type Node"""
        self.children: dict[Action: Node] = {}          
        """The children of the node - of type { Action: Node }"""
        self.fromAction: Action = Action(None) if fromAction == None else Action(fromAction, colorPicked=color, destinationsPicked=destDeal)
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

    def __init__(self, root: Node, simulations=5, pb_c_base=19652, pb_c_init=1.25) -> None:
        self.root: Node = root
        self.network: Network = Network(root.state.map)
        self.simulations = simulations
        self.pb_c_base = pb_c_base
        self.pb_c_init = pb_c_init
        self.root_dirichlet_alpha = 0.2
        self.root_exploration_fraction = 0.25
        self.search()

    def getValidMoves(self, state: State, previousAction: int=None, pickedUpWildFromFaceUp: bool=False) -> list[Action]:
        """Returns a list of type Action that are possible to take from a given state of type State
        
        previousAction - context parameter for use in actions that change the game state but not whose turn it is (drawing face up card)"""
        nextPlayer: Agent = state.players[state.currentPlayer]
        actionList: list[Action] = []
        zero = 0
        one = 0
        two = 0
        three = 0
        # Check for 0 - Placing trains
        if previousAction == None:
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
                    if color != 'WILD':
                        actionList.append(Action(1, colorPicked=[color]))
                        one += 1
                if len(state.trainCarDeck) >= 1:
                    actionList.append(Action(2))
                    two += 1
        elif previousAction == None or previousAction == 2:
            if len(state.faceUpCards) + len(state.trainCarDeck) >= 2:
                for color in state.faceUpCards:
                    actionList.append(Action(1, colorPicked=[color]))
                    one += 1
                if len(state.trainCarDeck) >= 1:
                    actionList.append(Action(2))
                    two += 1
        
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

        return actionList

    def ucb_score(self, parent: Node, child: Node) -> float:
        pb_c = math.log((parent.visitCount + self.pb_c_base + 1) / self.pb_c_base) + self.pb_c_init
        pb_c *= math.sqrt(parent.visitCount) / (child.visitCount + 1)
        U_sa = pb_c * child.priorProb
        Q_sa = child.getMeanWinningProb()
        return U_sa + Q_sa

    def select_child(self, node: Node) -> tuple[Action, Node]:
        """Selects the child based on the CPUCT formula in the AlphaGoZero paper"""
        max: tuple[int, Action, Node] = (0, None, None)
        for action, child in node.children.items():
            score = self.ucb_score(node, child)
            if score > max[0]:
                max = (score, action, child)
        return max[2]
    
    def evaluateNode(self, node: Node, network: Network) -> float:
        """Expands a current node, returns the probability of winning generated by the network"""
        a, Dc, Dd, Dr, w_p = network.play(node.state) # Get neural network forward pass evaluation
        policy = {}
        policySum = 0
        pickedWild = False
        if node.fromAction == 1:
            if node.fromAction.colorPicked != None:
                pickedWild = True if node.fromAction.colorPicked == ['WILD'] else False
        validMoves = self.getValidMoves(node.state, node.state.followUpFromMove, pickedWild)
        for action in validMoves:
            value = self.getValue(action, a, Dc, Dd, Dr, node.state.destinationDeal)
            policy[action] = value**2
            policySum += value
        for action, value in policy.items():
            newState, colorPicked, destDeal, endGame = self.newState(node.state, action)
            node.children[action] = Node(newState, priorProb=value/policySum, parent=node, fromAction=action.action, color=colorPicked, destDeal=destDeal)
        return w_p
    
    def newState(self, state: State, action: Action) -> State:
        """Takes a state and an action, and returns a new, deepcopied state which has carried out the action."""
        newGame = Game(state.map, state.players, False, False, False, state)
        newGame.performActionFrozen(newGame.players[state.currentPlayer], action)
        newState = State(newGame.board, newGame.faceUpCards, newGame.trainCarDeck, newGame.destinationsDeck, newGame.players, newGame.turn, newGame.mapName, newGame.movePerforming, newGame.wildFromFaceUp, newGame.destinationDeal, newGame.validGameMoves, newGame.actionMap)
        return newState, newGame.colorPicked, newGame.destinationDeal

    def getValue(self, action: Action, a: list[float], Dc: list[float], Dd: list[float], Dr: list[float], destDeal: list[list]) -> float:
        """Takes the ouput of the network and a valid action to take and returns a float representing how 'confident' the network is in making that move. The higher the float the higher the confidence."""
        a_p = a[action.action]
        Dc_p = 1
        Dd_p = 1
        if action.action == 0:
            for color in action.colorsUsed:
                Dc_p *= Dc[indexByColor[color]]
            Dr_p = Dr[action.routeToPlace[2]['index']]
            return product(a_p, Dc_p, Dr_p)
        elif action.action == 1:
            Dc_p = Dc[indexByColor[action.colorPicked[0]]]
            return product(a_p, Dc_p)
        elif action.action == 3:
            if action.destinationsPicked != None:
                for indexOfDeal in action.destinationsPicked:
                    Dd_p *= Dd[destDeal[indexOfDeal][3]]
                return product(a_p, Dd_p)
            else:
                return a_p
        elif action.action == 2:
            return a_p

    def backprop(self, searchPath: list[Node], win_p: float, toPlay: int):
        for node in searchPath:
            node.visitCount += 1
            if toPlay == node.state.currentPlayer:
                node.aggregateWinningProb += win_p
            else:
                node.aggregateWinningProb += (1-win_p)
    
    def addNoise(self, root: Node):
        actions = root.children.keys()
        noise = numpy.random.gamma(self.root_dirichlet_alpha, 1, len(actions))
        for action, noise in zip(actions, noise):
            root.children[action].priorProb = root.children[action].priorProb * (1 - self.root_exploration_fraction) + noise * self.root_exploration_fraction

    def search(self):

        self.evaluateNode(self.root, self.network)
        self.addNoise(self.root)

        for _ in range(self.simulations):
            currentNode = self.root # Start at the beginning
            searchPath: list[Node] = [currentNode] # The actions that have brought us to this state in MCTS

            while currentNode.isExpandedNode(): # If a node has children
                node: Node = self.select_child(currentNode) # Select one
                searchPath.append(node) # Add the child to the current path we are going down
                currentNode = node
            
            win_p = self.evaluateNode(currentNode, self.network)
            self.backprop(searchPath, win_p, searchPath[-1].state.currentPlayer)
            # print(len(searchPath))
            

            


    
