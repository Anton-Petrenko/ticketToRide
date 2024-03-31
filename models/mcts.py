"""
TODO: How do we denote actions in TTR MCTS?

Inputs:
1. Game Board (onehot for resnet)
2. Cards showing on the board (including destination)
3. Opponent maps (per player)
    a. train card hand size
    b. dest card hand size
4. Player map
    a. cards holding
    b. dest cards holding


Output Heads:
1. Action
2. Desire of color
3. Desire of destination cards
4. Desire of routes to claim
5. Prob. of winning

"""

class Node:
    """The nodes in the MCTS tree"""
    def __init__(self, prior, root=True) -> None:
        self.root = root
        self.prior = prior              # P(s,a)
        self.visitCount = 0             # N(s,a)
        self.aggregateWinningProb = 0   # W(s,a)
        self.children = list[Node]              
        """The children of the node - of type [ Node, Node, ... ]"""
        self.fromAction = list[list]
        """Each node that is a child stores the action (from its parent) that led to it - of type ???"""

    def getMeanWinningProb(self) -> float:
        """Return Q(s,a) - the mean winning probaility for a node/state"""
        if self.visitCount == 0:
            return float(0)
        return float(self.aggregateWinningProb / self.visitCount)

class MonteCarloSearch:
    """The Monte Carlo class for the Ticket to Ride Engine"""
    def __init__(self, root: Node) -> None:
        self.root = root

    def getValidMoves(self) -> tuple:
        """
        Determine the valid actions given a game state. Computes all the following:

        1. Place Trains - this action must denote the action number (0), which route is placeable, and which colors in the players hand it can be completed with as a list where the leftmost color is the majority color used. Rainbows in the color desire list are treated as an all-in (rainbow cards will always fill the available spots if possible).

        2. Draw Face Up - this action must denote the action number (1) and the colors picked up in a list where the leftmost color is the color picked first.

        3. Draw Face Down - this action must be denoted by the action number (2)

        4. Draw Destination Cards - this action must be denoted by the action number (3) and the destination cards possible to choose from.

        All these actions will be returned by a generator in the order of the list in this description

        """
        pass