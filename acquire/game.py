from acquire.board import *
from acquire.tiles import *
from acquire.player import *

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
    self.players = []

  def getId(self):
    return self.id

  def isStarted(self):
    return self.started

  def getPlayers(self):
    return len(self.players), self.players

  def addPlayer(self, player):
    if self.started:
      return False
    else:
      self.players.append(player)
      return True
   
  def start(self):
    if self.started:
      print("Game + " + self.ID + " already started!")
      return False
    elif len(self.players) < 3:
      print("Not enough players to start: " + str(len(self.players)))
      return False
     
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

  def serialize(self):
    return {
        'id': self.id,
        'started' : self.started,
        'players' : len(self.players),
     }
      
if __name__ == "__main__":
  game = Game(55)
  [game.addPlayer(Player(id)) for id in range(0,3)]
  game.start()

