from engine.run import play
from engine.players import Random
from copy import deepcopy

map = "USA"          # Map specification
games = 1            # Games to simulate
logs = True          # Basic logging to log.txt (only shows last played game)
debug = False        # Detailed logging to log.txt
drawGame = False     # See the game results (only relevant if simulating one game)
agents = [Random("Larry"), Random("David"), Random("Kevin")] # Player specification 

# MCTS Testing
ticketToRideGame = play(map, agents, logs, debug, games, drawGame)
# This game will stop at some point with 4% chance and do MCTS on that state