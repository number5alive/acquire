
# TileBag AI Player

## Project description

This fun project attempts to create a decent Acquire player using muzero-influenced reinforcement learning.
It is inspired by & forked from https://github.com/number5alive/acquire and designed to interface with its REST and websocket interfaces.

The aiplayer is designed in a way it can step in for any human player, read the game state, and submit its moves.

## Approach

The AIPlayer is first implemented using coarse game logic, with a view of replacing the game logic for each decision point by a machine learning component.

### Next steps

* Analyze traces for 4k game run
* play from loaded game state ?
* develop legal move logic for placing a tile
* run through neural network and alphazero tutorials
* encode gamestate for neural net
 * board has 12 x 9 = 108 tiles, and 7 hotels; by comparison with chess board encoding (8 x 8 x 2 players x 12 piece types), suggest we use 7 x 12 x 8 bits used for board state
 * also should encode own stocks hodlings, 7 x stocks left, money and stock value normalized (how can one normalize unbounded money?)
* build MCTS/nn training machine

## How to

1. clone this repo
2. setup and activate a python3 virtual environment
3. pip3 install -r requirements.txt for the game engine
4. pip3 install -r games/tilebag/aiplayer/requirements.txt for the AI player
5. python -m server to launch the tilebag server
6. in a different terminal window, ./create.sh to create a 4-player prototype game (default game name is thing5, default player names are Fred, Marc, Jean and Sonia)
7. for each of the player you wish to substitute by a robot, python -m games.tilebag.aiplayer.aiplayer <game> <player>
8. watch the game (using a browser, dial into http://localhost:5000/games/tilebag/thing5?playerid=d9414)

