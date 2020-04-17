from base import Game
from base import Player
from games.tiles import Tile, TileBag
from games.acquire.board import Board

class TileBagPlayer(Player):
  tiles=[]

  def __init__(self, id, name=None):
    print("init'ing a TileBag player")
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

  def run(self):
    if not super().run():
      print("Unable to start the game - probably not enough players")
      return False;
       
    print("TileBagGame Started!")
    self.board = Board(10,8)
    self.tilebag = TileBag(10,8)

    # give each player seven tiles to start
    print(self._players)
    for player in self._players:
      print("loop1")
      for i in range(0,7):
        print("take tile")
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
  print(tbg.serialize(True))

  """
  currBoard = tbg.getBoard()
  for row in currBoard:
    for col in row:
      print("{:^6}".format('X' if col else 'Y'), end=' ')
    print()
  """
