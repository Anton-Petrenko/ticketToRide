from engine.build import Simulate
from engine.players import Random
import time

map = "USA"         # Map specification
games = 100           # Games to simulate
logs = False         # Basic logging to log.txt (only shows last played game)
debug = False       # Detailed logging to log.txt
drawGame = False     # Visualize the game using matplotlib (only relevant if simulating one game)
agents = [Random("Random1"), Random("Random2"), Random("Random3"), Random("Random4")] # Player specification i 

# Run the engine
Simulate(map, agents, logs, debug, games, drawGame)