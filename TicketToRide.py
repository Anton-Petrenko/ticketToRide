from engine.build import Game, Simulate
from engine.players import Random

# Map specification
map = "USA"

# Player specification
agents = [Random(), Random(), Random()]

# Games to simulate - only works as 1 right now.
games = 1

# Run the engine
Simulate(map, agents, True, True, games)