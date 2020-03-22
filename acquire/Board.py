from Tiles import Tile

class Board:
  def __init__(self, rows, cols):
    self.rows=rows
    self.cols=cols
    self.tiles=[[False for row in range(0,self.rows)] for col in range(0,self.cols)]
    print(len(self.tiles[0]))
   
  def placeTile(self, tile):
    row, col = tile.getTilePos()
    self.tiles[row][col] = True

  def checkTile(self, row, col):
    return self.tiles[row,col]
     
  def __repr__(self):
    return str(self.tiles)
   
if __name__ == "__main__":
  board = Board(8,5)

  t=Tile(2,2)
  print(t)
  board.placeTile(t)
  print(board)
