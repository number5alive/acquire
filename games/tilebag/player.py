from games.tilebag.tiles import Tile

class Player:
  def __init__(self, id, name=None):
    self.id=id
    self.cash=6000
    self.tiles=[]
    self.stocks=[]
    if name is not None:
      self.name=name
    else:
      self.name="NoName"+str(id)

  def getId(self):
    return self.id

  def getName(self):
    return self.name

  def setName(self, name):
    self.name=name

  def playTile(self, t):
    pass

  def receiveTile(self, t):
    self.tiles.append(t)

  def __repr__(self):
    return 'Player ' + str(self.id) + ':$' + str(self.cash) + ',Tiles:' + str(self.tiles)
     
  def serialize(self):
    return {
        'id': self.id,
        'name': self.name,
        'num_tiles': len(self.tiles),
     }
 
if __name__ == "__main__":
  p=Player(17)

  t = Tile(7,7)
  p.receiveTile(t)

  print(p)
