from engine.build import Game
from engine.players import Random

# Map specification
map = "USA"

# Player specification
agents = [Random(), Random()]

# Run the game
Game(map, agents, True, False, drawGame=True)
