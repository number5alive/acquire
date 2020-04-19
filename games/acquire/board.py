from games.tiles import Tile

class Board:
  def __init__(self, rows, cols, tiles=[]):
    self.rows=rows
    self.cols=cols
    self.tiles=[[False for col in range(0,self.cols)] for row in range(0,self.rows)]
    for tile in tiles:
      self.placeTile(tile)

  def boardrows(self):
    for row in self.tiles:
      yield row
    return
   
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

  print("---- Testing a Board with Tiles already placed")
  board = Board(8,5,tiles=[Tile(3,3), Tile(1,1), Tile(2,2)])
  print(board)
#board = Board(12,5,tiles=[Tile.TileFromAlpha("1A"), Tile.TileFromAlpha("12E")])
  print(board)
