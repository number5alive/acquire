from games.tilebag.tiles import Tile

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

  # Important: presumes caller validates row/col
  def checkOccupied(self, row, col):
    return self.tiles[row][col]

  # Helper - tells us which positions U|D|R|L from us are occupied
  # eliminates a few unnecessary recursive steps, but also helpful on its own
  def checkNeighbours(self, row, col):
    conn=[]

    # check the rows above and below the supplied col
    for r in [row-1, row+1]:
        if self.isValidPos(r, col) and self.checkOccupied(r, col):
          conn.append(Tile.toAlpha((r, col)))
           
    # check the columns left and right of the supplied row
    for c in [col-1, col+1]:
      if self.isValidPos(row, c) and self.checkOccupied(row, c):
        conn.append(Tile.toAlpha((row, c)))

    return conn


  # Danger... Recursion! (and slow, unoptimized recursion at that!)
  # TODO: change the board to include bitmasking and do this right!
  def findConnected(self, conn, r, c):
    print("findConnected")
    if conn is None:
      conn=[]
       
    # Get alpha representation of tile position, and confirm it's valid
    curralpha=Tile.toAlpha((r,c))
    if self.alphaIsValid(curralpha):
      # if it's in the list already, no need to continue
      if curralpha in conn:
        return conn
         
      # it's not in the list already, so check if the space is occupied
      if not self.checkOccupied(r, c):
        return conn
         
      # okay, so it's occupied and not in the list, add it and check neighbours
      conn.append(curralpha)
      nb = self.checkNeighbours(r, c)
      for n in nb:
        if n not in conn:
          rnew, cnew = Tile.fromAlpha(n)
          conn = self.findConnected(conn, rnew, cnew)
       
    return conn;
     
  def boardrows(self):
    for row in self.tiles:
      yield row
    return
   
  def placeTile(self, tile):
    row, col = tile.getTilePos()
    self.tiles[row][col] = True
    

  def isValidPos(self, row, col):
    if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
      return False
    return True

  def alphaIsValid(self, alpha):
    row, col = Tile.fromAlpha(alpha)
    return self.isValidPos(row, col)

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
   
  print("---- Testing board helper functions ----")
  print("getsize: {}".format(board.getBoardSize()))
  print("checkTile(2,2): {}".format(not board.checkTile(2,2)))

  print("---- Testing Placing a tile ----")
  t=Tile(2,2)
  print("placed Tile" + str(t))
  board.placeTile(t)
  print(board)
  print("Occupied: {}".format(board.getOccupied()))

  print("---- Testing alphaIsValid ----")
  print("alphaIsValid: {}".format(board.alphaIsValid("1A")))
  print("!alphaIsValid: {}".format(not board.alphaIsValid("A1")))
  print("!alphaIsValid: {}".format(not board.alphaIsValid("9I")))
  print("isValidPos: {}".format(board.isValidPos(0, 1)))
  print("!isValidPos: {}".format(not board.isValidPos(110, 1)))
  print("!isValidPos: {}".format(not board.isValidPos(0, 110)))
  print("!isValidPos: {}".format(not board.isValidPos(0, -1)))
  print("!isValidPos: {}".format(not board.isValidPos(-1, 1)))

  print("---- Testing a Board with Tiles already placed")
  board = Board(8,5,tiles=[Tile(3,3), Tile(1,1), Tile(2,2)])
  print(board)
  print("Occupied: {}".format(board.getOccupied()))

  print("---- Testing findConnected logic ----")
  board.placeTile(Tile(4,4))
  board.placeTile(Tile(3,4))
  board.placeTile(Tile(3,3))
  board.placeTile(Tile(3,2))
  t=Tile(2,2)
  conn = board.findConnected(None, t.row, t.col)
  print("{} is in this set of connected: {}".format(t, conn))
  print("{} has neighbours at {}".format(Tile(2,3), board.checkNeighbours(2, 3)))

  print("---- Testing Serialization and save/restore ----")
  saved=board.serialize()
  print("Serialized: {}".format(saved))
  newboard=Board.loadFromSavedData(saved)
  print("Restored == Saved?: {}".format(saved == newboard.serialize()))
  newboard.placeTile(Tile(0,0))
