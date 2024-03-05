"""
1. BUILD THE BOARD with networkx
    a. MultiGraph - multiples edges between the same nodes
        a1. Note: Only one claimable edge in games of 2 or 3 people
    b. Use list of all destinations to make it
    c. Edges (Paths) between Nodes (Destinations) have a weight that corresponds to how many trains long it is
    d. Edges (Paths) between Nodes (Destinations) have a required color assigned to them as well

2. BUILD THE DECKS
    Colors: Pink, White, Blue, Yellow, Orange, Black, Red, Green
    a. Train Car Cards as a queue (110 total, 12 of each color, 14 wild cards)
    b. Destination Cards as a queue (map dependent)

3. INITIALIZE THE GAME
    a. Each player gets 4 Train Car Cards to start
    b. Each player is then dealt 3 destination cards and chooses at least 2
        b1. Returned cards get placed back into the queue

4. PLAY THE GAME
    a. Need a function that generates valid moves
    b. Need a function that executes a given move
    c. NOTES:
        - Drawing Destination Cards means that player receives 3 and must choose at least 1


5. SCORE THE GAME
    Route Scoring:
    1 Car   1 Point
    2 Cars  2 Points
    3 Cars  4 Points
    4 Cars  7 Points
    5 Cars  10 Points
    6 Cars  15 Points

    Longest Route: 10 Points
"""