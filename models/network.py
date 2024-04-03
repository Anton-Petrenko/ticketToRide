from engine.build import State
from engine.data import listColors
from engine.players import Agent

class Network:
    """The actual network object that powers the AI agent"""
    def __init__(self, map: str) -> None:
        self.map = map
    
    def formatInput(self, destAvail, destHand, destPerPlayer, routesTaken, colorsAvail, colorsPerPlayer) -> list[int]:
        """Format game state data into input for the network - input type unknown for now"""
        
    
    def play(self, state: State):
        """
        Tell the network to evaluate a game state

        Input - a state of type State (turns into one long vector of [avail. dest] + [dest. in hand] + [dest. count/player] + [routes taken] + [avail. colors] + [colors/player])

        Outputs - (a, Dc, Dd, Dr, W)

        a = action to take

        Dc = desire of colors
        
        Dd = desire of destinations

        Dr = desire of routes

        W = win probability from state
        """
        # Transform state into network input

        # 1. Available Destinations
        destAvail = [0]*30 # 30 destination cards in USA map
        if state.followUpFromMove == 3:
            destDealRaw = [state.destinationDeck.pop(), state.destinationDeck.pop(), state.destinationDeck.pop()]
            for destination in destDealRaw:
                destAvail[destination[3]]=1
        
        #2. Destinations in Hand
        currentPlayer: Agent = state.players[state.currentPlayer]
        destHand = [0]*30 # 30 destination cards in USA map
        for destination in currentPlayer.hand_destinationCards:
            destHand[destination[3]]=1
        
        #3. Destination count per opponent [next to go, after, etc.], must be of length three padded with zeros ENDED HERE
        destCount = []
        for i in range(state.currentPlayer + 1, state.currentPlayer + len(state.players)):
            destCount.append(len(state.players[i % len(state.players)].hand_destinationCards))
        while len(destCount) != 3:
            destCount.append(0)
        
        #4. Routes Taken per player [current, next to go, after, etc.]
        routesTaken = []
        for i in range(state.currentPlayer, state.currentPlayer + len(state.players)):
            taken = [0]*100 # 100 routes in USA map
            edges = [edge for edge in state.board.edges(data=True) if edge[2]['owner'] == i % len(state.players)]
            for edge in edges:
                taken[edge[2]['index']] = 1
            routesTaken += taken

        #5. Available colors
        colorsAvail = [] # 9 colors in game
        for color in listColors():
            colorsAvail.append(state.faceUpCards.count(color))

        #6. Colors / Player (TODO: check the accuracy of the card counting for opponents AND ordering at some point)
        colorsCount = [currentPlayer.hand_trainCards.count(color) for color in listColors()]
        for i in range(state.currentPlayer + 1, state.currentPlayer + len(state.players)):
            colorsCount += currentPlayer.colorCounting[i % len(state.players)]
        while len(colorsCount) != 39:
            colorsCount.append(0)

        quit()
