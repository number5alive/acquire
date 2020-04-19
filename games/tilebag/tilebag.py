from base import Game
from base import Player
from games.tiles import Tile, TileBag
from games.acquire.board import Board
from itertools import cycle, islice
from random import shuffle

class TileBagPlayer(Player):
  _tiles=[]

  def __init__(self, id, name=None):
    super().__init__(id)
    self._tiles = []

  def receiveTile(self, tile):
    self._tiles.append(tile)

  # this only exists to help program the tests
  # We'll need a way for the user to specify which tile they're playing
  # NOTE: We don't pop it, the game will do that if it's a valid move
  def selectRandomTile(self):
    shuffle(self._tiles)
    return self._tiles[0]

  def removeTile(self, tile):
    self._tiles.remove(tile)

  @property
  def tiles(self):
    return self._tiles

  def savePlayerData(self):
    return {'tiles': self._tiles}

class TileBagGame(Game):
  _name='TileBag'
  _minPlayers=3
  _maxPlayers=5
  _currPlayer=0
  _playerClass=TileBagPlayer
  _starturl='/tilebag/v1'
  board=[]
  tilebag=None;
   
  def __init__(self, id):
    super().__init__(id)

  def getBoard(self):
    return self.board

  @property
  def currPlayer(self):
    return self._currPlayer

  def getPlayerInfo(self, playerid):
    pass

  def run(self):
    if not super().run():
      print("Unable to start the game - probably not enough players")
      return False;
       
    # Initialize Game Components
    print("TileBagGame Started!")
    self.board = Board(10,8)
    self.tilebag = TileBag(10,8)

    # Determine Start Order: draw a single tile for each player
    self._currPlayer = None
    lowestTile=Tile(10,8)
    for player in self._players:
      t=self.tilebag.takeTile()
      if t <= lowestTile:
        lowestTile=t
        self._currPlayer=player
      self.board.placeTile(t)

    # Now set the game order to the above
    self._rotation = islice(cycle(self._players), self._players.index(self._currPlayer)+1, None)
   
    # give each player seven tiles to start
    print(self._players)
    for player in self._players:
      for i in range(0,7):
        player.receiveTile(self.tilebag.takeTile())

  def playTile(self, playerId, tile):
    if self._started:
      if self._currPlayer.getId() == playerId:
        if tile in self._currPlayer.tiles:
          self.board.placeTile(tile)
          # TODO: ensure the above succeeds and is a valid move
          self._currPlayer.removeTile(tile)
          self._currPlayer.receiveTile(self.tilebag.takeTile())
          self._currPlayer=next(self._rotation)
        else:
          print("{} is not in {}".format(tile, self._currPlayer.tiles))
      else:
        print("{} is not the current player".format(playerId))
    else:
      print("game isn't started, cannot make a move")

  def saveGameData(self):
    return { 
      'board': self.board,
      'bag': self.tilebag,
    }

if __name__ == "__main__":
  # helper function to show the board state in the console
  def printBoard(board):
    i=1
    print("{:^6}".format(""), end=' ')
    print(*("{:^6}".format(chr(x+ord('A'))) for x in range(0,8)))
    for row in currBoard.boardrows():
      print("{:^4}: ".format(i), end=' ')
      for col in row:
        print("{:^6}".format(col), end=' ')
      print()
      i+=1
       
  print("name: " + TileBagGame.name())
  print("min: " + str(TileBagGame.minPlayers()))
  print("max: " + str(TileBagGame.maxPlayers()))
  print("fullname: " + TileBagGame.fullname())

  # Initialize a new game, with three players, and start it
  tbg=TileBagGame(1)
  tbg.addPlayer(tbg.newPlayer(1))
  tbg.addPlayer(tbg.newPlayer(2))
  tbg.addPlayer(tbg.newPlayer(3))
  tbg.run()

  currBoard = tbg.getBoard()
  printBoard(currBoard)
  print("{} is the starting player".format(tbg.currPlayer.name))

  # simulate a bunch of turns
  for i in range(0,40):
    print("{} tiles: {}".format(tbg.currPlayer.name, tbg.currPlayer.tiles))
    tile=tbg.currPlayer.selectRandomTile()
    tbg.playTile(tbg.currPlayer.getId(), tile)
   
  printBoard(currBoard)
   
