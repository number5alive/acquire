import random

class Tile:
  """
  A single Tile
  """

  def __init__(self, row, col):
    self.row = row
    self.col = col

  def __repr__(self):
    """
    Rebase tile to People-speak
    """
    return chr(self.row+65) + str(self.col+1)

class TileBag:
  """
  A Bag of Tiles - Randomized from the start
  """
  def __init__(self, numRows, numCols):
    self.bag = [Tile(row, col) for row in range(0,numRows) 
                               for col in range(0,numCols)]
    random.shuffle(self.bag)
                                  
  def __repr__(self):
    return "Bag = " + str(self.bag)

  def isEmpty(self):
    return len(self.bag) == 0

  """
  The following is not safe... make sure callers check "isEmpty"
  """
  def takeTile(self):
    return self.bag.pop()

if __name__ == "__main__":
  bag = TileBag(5,5)
  print(bag)

  while not bag.isEmpty():
    t=bag.takeTile()
    print(t)
