from Board import *
from Tiles import *
from Player import *

#Define the game constants
BOARD_ROWS=8
BOARD_COLS=12
TILE_MAX=7
 
def gameLoop(players):
  run=True

  # initialize the game: board, tiles, players, stocks
  board = Board(BOARD_ROWS, BOARD_COLS)
  bag = TileBag(BOARD_ROWS, BOARD_COLS)

  # TODO: Define starting player (draw single tile)
  for player in players:
    t=bag.takeTile()
    board.placeTile(t)

  # Give each player their starting tiles
  for player in players:
    for i in range(0,TILE_MAX):
      player.receiveTile(bag.takeTile())
   
  while run:
    # Each player takes their turn (TODO: enforce turn order)
    for player in players:
      # TODO: Play tile
      # TODO: Buy stocks
      # TODO: Take tile
      pass
    run=False # kill it for now

  print(board)
  print(players)
      
if __name__ == "__main__":
  players = [Player(id) for id in range(0,3)]
  gameLoop(players)

