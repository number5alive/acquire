import random
import base

class Tile:
  """
  A single Tile
  """

  def __init__(self, row, col):
    self._row = row
    self._col = col

  @property
  def row(self):
    return self._row

  @property 
  def col(self):
    return self._col

  # returns the row/column when given an alpha representation
  # presumes alpha will be in format [1-9]*[A-F]
  # TODO add check to confirm alpha format
  @staticmethod
  def fromAlpha(alpha):
    # somewhat annoyingly I've decided the alpha is col then row, so revered here
    # AND the arrays start at Zero, but we show starting from One for ppl
     
    # Validate the alpha fits the pattern
    colpart=alpha[0:-1]
    rowpart=alpha[-1]
    if not colpart.isnumeric() or not rowpart.isupper():
      return -1, -1
       
    col = int(alpha[0:-1])-1             # all except the last charater
    row = (ord(alpha[-1]) - ord('A'))    # last character, rebased
    return row, col

  @staticmethod
  def newTileFromAlpha(alpha):
    row, col = Tile.fromAlpha(alpha)
    return Tile(row, col)

  @staticmethod
  def toAlpha(rowcol):
    row=rowcol[0]
    col=rowcol[1]
    return str(col+1) + chr(row+65)

  def __eq__(self, other):
    return self._row == other.row and self._col == other.col

  def __lt__(self, other):
    return self._row < other.row or (self._row == other.row and self._col < other.col)
  def __le__(self, other):
    return self.__lt__(other) or self.__eq__(other)

  def __gt__(self, other):
    return self._row > other.row or (self._row == other.row and self._col > other.col)

  def getTilePos(self):
    return self._row, self._col

  def serialize(self):
    return Tile.toAlpha((self._row, self._col))

  def __repr__(self):
    """
    Rebase tile to People-speak
    """
    return Tile.toAlpha((self._row, self._col))

class TileBag:
  """
  A Bag of Tiles - Randomized from the start
  """
  def __init__(self, numRows, numCols, initialTiles=None):
    if initialTiles is None:
      self.bag = [Tile(row, col) for row in range(0,numRows) 
                               for col in range(0,numCols)]
      random.shuffle(self.bag)
    else:
      self.bag = []
      for tile in initialTiles:
        self.bag.append(Tile.newTileFromAlpha(tile))

  def isEmpty(self):
    return len(self.bag) == 0

  """
  The following is not safe... make sure callers check "isEmpty"
  """
  def takeTile(self):
    if len(self.bag) > 0:
      return self.bag.pop()
    else:
      return None

  def serialize(self):
    return [t.serialize() for t in self.bag]
     
"""
  def __repr__(self):
    print("Tile.__repr__")
    return str(self.bag)
    """

if __name__ == "__main__":
  print("---- Testing basic tile and tilebag functionality ----")
  bag = TileBag(5,5)
  print(bag)

  t=bag.takeTile()
  print(str(t.getTilePos()) + ' ' + str(t))
  print("Tile {} is ({},{})".format(t, t.row, t.col))
   
  while not bag.isEmpty():
    t=bag.takeTile()

  print("---- Testing Tile equivalences ----")
  t1 = Tile(7,7)
  t2 = Tile(7,7)
  t3 = Tile(8,8)

  print(t1 == t2)
  print(t1 != t3)
  print(t2 != t3)
  print(t3 == Tile(8,8))

  print("---- Testing tile transforms to/from its alpha representation ----")
  testalpha=["1A", "1B", "12J", "5E", "9C"]
  testpos=[(0,0), (0,1), (4,4), (9,11)]
  print(*(x + " test " + str(x == str(Tile.toAlpha(Tile.fromAlpha(x)))) for x in testalpha), sep='\n')
  print(*(str(x) + " test " + str(str(x) == str(Tile.fromAlpha(Tile.toAlpha(x)))) for x in testpos), sep='\n')
  print("1B is " + str(Tile.fromAlpha("1B")))
  print("1,0 is " + str(Tile.toAlpha((1,0))))
