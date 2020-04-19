from base import Game
from base import Player
from games.tiles import Tile, TileBag
from games.acquire.board import Board

class TileBagPlayer(Player):
  tiles=[]

  def __init__(self, id, name=None):
    super().__init__(id)
    self.tiles = []

  def receiveTile(self, tile):
    self.tiles.append(tile)

  def savePlayerData(self):
    return {'tiles': self.tiles}

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
       
    # Initialize Components
    print("TileBagGame Started!")
    self.board = Board(10,8)
    self.tilebag = TileBag(10,8)

    # Determine Start Order: draw a single tile for each player
    self._currPlayer = None
    lowestTile=Tile(10,8)
    for player in self._players:
      t=self.tilebag.takeTile()
      print(t)
      if t <= lowestTile:
        print("{} is the current lowest".format(t))
        lowestTile=t
        self._currPlayer=player
      self.board.placeTile(t)
   
    # give each player seven tiles to start
    print(self._players)
    for player in self._players:
      for i in range(0,7):
        player.receiveTile(self.tilebag.takeTile())

  def saveGameData(self):
    return { 
      'board': self.board,
      'bag': self.tilebag,
    }

if __name__ == "__main__":
  print("name: " + TileBagGame.name())
  print("min: " + str(TileBagGame.minPlayers()))
  print("max: " + str(TileBagGame.maxPlayers()))
  print("fullname: " + TileBagGame.fullname())

  tbg=TileBagGame(1)
  print(tbg.serialize(True))
  tbg.addPlayer(tbg.newPlayer(1))
  tbg.addPlayer(tbg.newPlayer(2))
  tbg.addPlayer(tbg.newPlayer(3))
  tbg.run()

  def printBoard(board):
    i=1
    print("{:^6}".format(""), end=' ')
    print(*("{:^6}".format(chr(x+ord('A'))) for x in range(0,8)))
    for row in currBoard.boardrows():
      print("{:^4}: ".format(i), end=' ')
      for col in row:
        #print("{:^6}".format('X' if col else 'Y'), end=' ')
        print("{:^6}".format(col), end=' ')
      print()
      i+=1
       
  currBoard = tbg.getBoard()
  printBoard(currBoard)
  print("{} is the starting player".format(tbg.currPlayer.name))

