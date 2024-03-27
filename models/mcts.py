class Node:
    """The nodes in the MCTS tree"""
    def __init__(self, prior, root=True) -> None:
        self.root = root
        self.prior = prior              # P(s,a)
        self.visitCount = 0             # N(s,a)
        self.aggregateWinningProb = 0   # W(s,a)
        self.children = [Node]              
        """The children of the node - of type [ Node, Node, ... ]"""
        self.fromAction = list[list]
        """Each node that is a child stores the action (from its parent) that led to it - of type (p, Dc, Dd)"""

    def getMeanWinningProb(self):
        """Return Q(s,a) - the mean winning probaility for a node/state"""
        if self.visitCount == 0:
            return 0
        return self.aggregateWinningProb / self.visitCount

class MonteCarloSearch:
    """The Monte Carlo class for the Ticket to Ride Engine"""
    def __init__(self) -> None:
        pass