from engine.build import Simulate
from engine.players import Random

map = "USA"          # Map specification
games = 1         # Games to simulate
logs = False         # Basic logging to log.txt (only shows last played game)
debug = False        # Detailed logging to log.txt
drawGame = True     # See the game results (only relevant if simulating one game)
agents = [Random("Larry"), Random("David")] # Player specification i 

# Run the engine
Simulate(map, agents, logs, debug, games, drawGame)