from Tiles import Tile

class Player:
  def __init__(self, id):
    self.id=id
    self.cash=6000
    self.tiles=[]
    self.stocks=[]

  def playTile(self, t):
    pass

  def receiveTile(self, t):
    self.tiles.append(t)

  def __repr__(self):
    return 'Player ' + str(self.id) + ':$' + str(self.cash) + ',Tiles:' + str(self.tiles)
     
if __name__ == "__main__":
  p=Player(17)

  t = Tile(7,7)
  p.receiveTile(t)

  print(p)
