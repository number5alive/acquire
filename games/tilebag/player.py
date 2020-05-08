from games.tilebag.tiles import Tile, TileBag
from base import Player
from random import shuffle

class TileBagPlayer(Player):
  _tiles=[]
  _stocks=[]

  def __init__(self, id, name=None, money=6000):
    super().__init__(id, name=name)
    self._startmoney = money
    self._initcomponents()
     
  def __del__(self):
    print("Deleting TileBagPlayer")

  def _initcomponents(self):
    self._tiles = []
    self._stocks = []
    self.money = self._startmoney

  def reset(self):
    del self._tiles
    del self._stocks
    self._initcomponents()

  # this only exists to help program the tests
  # We'll need a way for the user to specify which tile they're playing
  # NOTE: We don't pop it, the game will do that if it's a valid move
  def selectRandomTile(self):
    if len(self._tiles) > 0:
      shuffle(self._tiles)
      return self._tiles[0]
    else:
      return None

  def receiveTile(self, tile):
    self._tiles.append(tile)

  def removeTile(self, tile):
    self._tiles.remove(tile)

  def numStocks(self, hname=None):
    if hname is None:
      return len(self._stocks)
    else:
      count=0
      for s in self._stocks:
        if s.name == hname:
          count+=1
      return count

  def receiveStock(self, stock):
    self._stocks.append(stock)

  def returnStock(self, sname):
    for s in self._stocks:
      if s.name == sname:
        self._stocks.remove(s)
        return s
    return None

  @property
  def tiles(self):
    return self._tiles

  def loadFromSavedData(self,sd):
    self._name=sd['name']
     
    pd=sd['playerdata']
    for tile in pd['tiles']:
      t=Tile.newTileFromAlpha(tile)
      self._tiles.append(t)
     
  def savePlayerData(self):
    # recover unique names in our list of stocks
    snames={s.name for s in self._stocks}
    return {
      'tiles': [t.serialize() for t in self._tiles],
      'money': self.money,
      'stocks': { s : sum(x.name == s for x in self._stocks) for s in snames},
      }
       
if __name__ == "__main__":
  p=TileBagPlayer(100, "Stan", money=7000)

  # TODO: add a bunch of unit tests (most are covered now in tilebag.py
   
  print("---- Testing TileBagPlayer functionality ----")
  print("savePlayerData: {}".format(p.savePlayerData()))
   
