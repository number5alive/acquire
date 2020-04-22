from games.tiles import Tile

class Board:
  def __init__(self, rows, cols, tiles=[], initialState=None):
    self.rows=rows
    self.cols=cols
    self.tiles=[[False for col in range(0,self.cols)] for row in range(0,self.rows)]
    if initialState:
      for alpha in initialState:
        self.placeTile(Tile.newTileFromAlpha(alpha))
       
    for tile in tiles:
      self.placeTile(tile)

  @staticmethod
  def loadFromSavedData(sd):
    return Board(sd['nrows'],sd['ncols'],initialState=sd['occupied'])

  # Return a list of occupied rows (in alpha representation)
  def getOccupied(self):
    occupied=[]
    for row in range(0,self.rows):
      for col in range(0,self.cols):
        if self.tiles[row][col]:
          occupied.append(Tile.toAlpha((row,col)))
    return occupied
     
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

  def serialize(self):
    return { 
      'nrows' : self.rows,
      'ncols' : self.cols,
      'occupied' : self.getOccupied(),
      }
     
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
  print("Occupied: {}".format(board.getOccupied()))

  print("---- Testing a Board with Tiles already placed")
  board = Board(8,5,tiles=[Tile(3,3), Tile(1,1), Tile(2,2)])
  print(board)
  print("Occupied: {}".format(board.getOccupied()))

  print("---- Testing Serialization and save/restore ----")
  saved=board.serialize()
  print("Serialized: {}".format(saved))
  newboard=Board.loadFromSavedData(saved)
  print("Restored == Saved?: {}".format(saved == newboard.serialize()))
  newboard.placeTile(Tile(0,0))
