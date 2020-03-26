from Board import *
from Tiles import *
from Player import *

class Game:
  #Define the game constants
  BOARD_ROWS=8
  BOARD_COLS=12
  TILE_MAX=7

  def __init__(self, id):
    # initialize the game: board, tiles, players, stocks
    self.id = id
    self.board = Board(Game.BOARD_ROWS, Game.BOARD_COLS)
    self.bag = TileBag(Game.BOARD_ROWS, Game.BOARD_COLS)
    self.started = False

  def getId(self):
    return self.id

  def serialize(self):
    return {
        'id': self.id,
        'started' : self.started,
     }
   
  def start(self, players):
    if self.started:
      print("Game + " + self.ID + " already started!")
      return False
     
    self.players = players
    self.started=True

    # TODO: Define starting player (draw single tile)
    for player in self.players:
      t=self.bag.takeTile()
      self.board.placeTile(t)

    # Give each player their starting tiles
    for player in self.players:
      for i in range(0,Game.TILE_MAX):
        player.receiveTile(self.bag.takeTile())
     
    while self.started:
      # Each player takes their turn (TODO: enforce turn order)
      for player in self.players:
        # TODO: Wait for Player to Play tile
        # TODO: Wait for Player to Buy stocks
        # TODO: Wait for Player to Take tile
        pass
      self.started=False # kill it for now

    print(self.board)
    print(self.players)
      
if __name__ == "__main__":
  players = [Player(id) for id in range(0,3)]
  game = Game(55)
  game.start(players)

