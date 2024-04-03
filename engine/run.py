import time
from engine.build import Game, State
from engine.players import Agent
from models.mcts import MonteCarloSearch, Node


def play(map: str, players: list[Agent], logs: bool, debug: bool, runs: int, drawGame: bool) -> Game:
    """
    Play a single or batch of Ticket to Ride games using the engine
    
    map - "USA"

    games - # of games to simulate

    agents - a list of 2-4 agents available: "Random"

    logs - print the logs to log.txt (if multiple games simulated, will only print last one)

    debug - add more descriptive statements to the logs

    drawGame - only for single-game simulations, will draw the final game map using matplotlib
    """

    game = None 
    iterations = runs

    if runs == 1:
        game = Game(map, players, logs, debug, drawGame)

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
    
    # Testing MCTS
    state = State(game.board, game.faceUpCards, game.trainCarDeck, game.destinationsDeck, game.players, game.turn, game.mapName, game.movePerforming)
    MonteCarloSearch(Node(state))