from Tiles import Tile

class Board:
  def __init__(self, rows, cols):
    self.rows=rows
    self.cols=cols
    self.tiles=[[False for col in range(0,self.cols)] for row in range(0,self.rows)]
   
  def placeTile(self, tile):
    row, col = tile.getTilePos()
    self.tiles[row][col] = True

  def checkTile(self, row, col):
    return self.tiles[row][col]

  def getBoardSize(self):
    return self.rows, self.cols
     
  def __repr__(self):
    return str(self.tiles)
   
if __name__ == "__main__":
  board = Board(8,5)
   
  print("---- Testing getBoardSize")
  print(board.getBoardSize())

  print("---- Testing checkTile(2,2)")
  print(board.checkTile(2,2))

  print("---- Testing Placing a tile")
  t=Tile(2,2)
  print("placed Tile" + str(t))
  board.placeTile(t)
  print(board)
