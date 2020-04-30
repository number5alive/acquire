from base import Game
from base import Player
from games.tilebag.tiles import Tile, TileBag
from games.tilebag.board import Board
from games.tilebag.hotels import Hotel, Stock
from itertools import cycle, islice
from random import shuffle

class TileBagPlayer(Player):
  _tiles=[]
  _stocks=[]

  def __init__(self, id, name=None, money=6000):
    super().__init__(id, name=name)
    self._tiles = []
    self._stocks = []
    self.money = money
     
  def __del__(self):
    print("Deleting TileBagPlayer")

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

class TileBagGame(Game):
  # Fixed Data about the Game
  _HOTELS=["Worldwide", "Saxxon", "Festival", "Imperial", "American", "Continental", "Tower"]
  _name='TileBag'
  _minPlayers=3
  _maxPlayers=5
  _playerClass=TileBagPlayer
  _starturl='/tilebag/v1'
   
  def __init__(self, id):
    super().__init__(id)
    self._conflictTiles=[]
    self.board=[]
    self._currPlayer=None
    self.tilebag=None;
    self.hotels=[Hotel(name) for name in self._HOTELS]

  def __del__(self):
    # todo, delete all of our things
    print("Deleting TileBagGame")
    super().__del__()

  def getBoard(self):
    return self.board

  @property
  def currPlayer(self):
    return self._currPlayer

  def _getPlayer(self, playerid):
    for player in self._players:
      if player.getId() == playerid:
        return player
    return None

  def getPlayerInfo(self, playerid):
    player=self._getPlayer(playerid)
    if player:
      return player.serialize(True)
    return None

  def run(self):
    if not super().run():
      print("Unable to start the game - probably not enough players")
      return False;
       
    # Initialize Game Components
    print("TileBagGame Started!")
    self.board = Board(9,12)
    self.tilebag = TileBag(9,12)

    # Determine Start Order: draw a single tile for each player
    self._currPlayer = None
    lowestTile=Tile(10,8)
    for player in self._players:
      t=self.tilebag.takeTile()
      if t <= lowestTile:
        lowestTile=t
        self._currPlayer=player
      self.board.placeTile(t)

    # Now set the game order to the above
    self._rotation = islice(cycle(self._players), self._players.index(self._currPlayer)+1, None)
   
    # give each player seven tiles to start
    for player in self._players:
      for i in range(0,7):
        player.receiveTile(self.tilebag.takeTile())

  def moneyAction(self, playerId, amount):
    if self._started:
      player=self._getPlayer(playerId)
      if player and type(amount) is int:
        if amount > 0 or player.money >= -amount:
          player.money += amount
          return True
        else:
          print("moneyAction: Subtracting more than the player has")

    return False

  def _getHotelByName(self, hname):
    for h in self.hotels:
      if h.name == hname:
        return h
    return None

  # return or take stocks from the pile
  def stockAction(self, playerId, hotel, amount):
    if self._started:
      player=self._getPlayer(playerId)
      if player and type(amount) is int:
        h=self._getHotelByName(hotel)
        if h is not None:
          if amount > 0:
            return self._takeStocks(player, h, amount)
          elif amount < 0:
            return self._returnStocks(player, h, -amount)
    return False

  def _takeStocks(self, player, h, amount):
    if h.stocksRemaining() >= amount:
      for i in range(0,amount):
        s=h.takeStock()
        player.receiveStock(s)
      return True
    return False
       
  def _returnStocks(self, player, h, amount):
    if player.numStocks(hname=h.name) >= amount:
      for i in range(0,amount):
        s=player.returnStock(h.name)
        if not h.returnStock(s):
          return False
      return True
    return False

  # set alpha to None to remove it from the board
  # set it to a tile position to place it on the board
  def placeHotel(self, playerId, hotel, alpha):
    if self._started:
      # NOTE: For now we're letting anyone move the hotels
      #if self._currPlayer.getId() == playerId:
   
      h=self._getHotelByName(hotel)
      if h is not None:
        # REMOVE HOTEL - If it's a remove, resolve conflictTiles
        if alpha is None:
          # remove the hotel from the board
          h.setPosition(None, occupies=None)

          # resolve any conflict tiles
          self.updateConflictTiles()
           
          return True
        
        # ADD HOTEL - if it's an add, determine what spaces it occupies
        elif self.board.alphaIsValid(alpha):
          # find the full list of connected tiles
          r, c = Tile.fromAlpha(alpha)
          conn = self.board.findConnected(None, r, c, skip=self._conflictTiles)
          print("Connected to {} is: {}".format(alpha, conn))
           
          # TODO: make sure there are at least two connected tiles
          h.setPosition(alpha, occupies=conn)
          return True
        else:
          print("Invalid Hotel Alpha / or Move")
      else:
        print("Invalid Hotel name")
    
    return False

  # loop through the conflict tiles and see if any are no longer in conflict
  def updateConflictTiles(self):
    for cf in self._conflictTiles:
      self.checkTileNextToHotel(cf)

  def checkTileNextToHotel(self, tile):
    # find neighbouring occupied spaces
    conn=self.board.checkNeighbours(tile.row, tile.col)
    hn=[]
    for h in self.hotels:
      if h.occupies is not None:
        # check if this space neighbours any active hotels
        tmp = [o for o in conn if o in h.occupies]
        if len(tmp) > 0:
          print("new tile at {} is adjacent to {}".format(tile, h.name))
          hn.append(h)

    # Now hn has the list of neighbouring hotels
    if len(hn) >= 2:
      # it's more than one hotel - add it to a "conflict" list 
      print("{} is between these hotels: {}".format(tile, [h.name for h in hn]))
      if tile not in self._conflictTiles:
        self._conflictTiles.append(tile)
    elif len(hn) == 1:
      print("{} is only adjacent to this hotels: {}".format(tile, hn[0].name))
      # just one hotel, so update that hotel's connected list
      if tile in self._conflictTiles:
        print("removing conflict tile: {}".format(tile))
        self._conflictTiles.remove(tile)
        hn[0].setOccupies(self.board.findConnected(None, tile.row, tile.col, skip=self._conflictTiles))
    else:
      # this would happen for each "safe" new tile placed
      if tile in self._conflictTiles:
        self._conflictTiles.remove(tile)
       
  def playTile(self, playerId, tile=None, alpha=None):
    if tile is None and alpha is not None:
      tile=Tile.newTileFromAlpha(alpha)
       
    if self._started:
      if self._currPlayer.getId() == playerId:
        if tile in self._currPlayer.tiles:
          # NOTE: this tile MIGHT be between two tiles, in that case we need
          #       to ensure it doesn't cause a "merger" until one of those
          #       hotels gets removed, therefore:
           
          # put tile on the board, and presume it'll be between two tiles
          self.board.placeTile(tile)
          self._conflictTiles.append(tile)

          # now verify that fact for this tile, cleanup if we were wrong
          self.checkTileNextToHotel(tile)

          # TODO: ensure the above succeeds and is a valid move
          self._currPlayer.removeTile(tile)
          print("Played Tile: {}".format(tile))
          if self.tilebag.isEmpty():
            print("Tilebag exhausted, trigger end-game state")
          else:
            self._currPlayer.receiveTile(self.tilebag.takeTile())
          self._currPlayer=next(self._rotation)
          return True
        else:
          print("{} is not in {}".format(tile, self._currPlayer.tiles))
      else:
        print("{} is not the current player".format(playerId))
    else:
      print("game isn't started, cannot make a move")

    # if we get down here, we didn't succeed at playing the tile
    return False

  # Load (recreate) a version of this game from the JSON object
  def loadFromSavedData(self,sd):
    gd=sd['gamedata']
     
    # create the players
    for player in sd['players']:
      p=self.newPlayer(player['id'])
      p.loadFromSavedData(player)
      self.addPlayer(p)
      if player['id'] == gd['currPlayer']:
        self._currPlayer=p

    # restore the game state
    self._started=sd['started']
    self._rotation = islice(cycle(self._players), self._players.index(self._currPlayer)+1, None)
     
    # restore the board and the tilebag
    self.board=Board.loadFromSavedData(gd['board'])
    rows, cols =self.board.getBoardSize()
    self.tilebag=TileBag(rows, cols, initialTiles=gd['bag'])
   
  # Saves the game to json format (using the JSONEncoder from elsewhere)
  # Why is this different than getPublicInformation? Because I'm super lazy!
  # TODO: find a cute way to merge these
  def saveGameData(self):
    if self._started:
      return { 
        'currPlayer': self._currPlayer.getId(),
        'board': self.board.serialize(),
        'bag': self.tilebag.serialize(),
        'hotels': [h.serialize() for h in self.hotels]
      }
    else:
      return {}
     
  # Get the information you'd see if you were looking at this game on a table
  def getPublicInformation(self):
    return {
      'currPlayer': self._currPlayer.serialize(False),
      'board': self.board.serialize(),
      'players' : [x.serialize(False) for x in self._players],
      'hotels': [h.serialize() for h in self.hotels]
    }

SAVEDGAME="game.json"
if __name__ == "__main__":
  import os
  import json
  import base

  print("---- Testing restoring state from json ----")
  if os.path.isfile(SAVEDGAME):
    print("save file is there, let's give it a try")
    with open(SAVEDGAME, 'r') as f:
      sd=json.load(f)
      tbg=TileBagGame(sd['id'])
      tbg.loadFromSavedData(sd)
      tbg_sd=json.dumps(tbg.serialize(True))
      sd_js=json.dumps(sd)
      #if str(sd) == str(tbg.serialize(True)):
      if str(sd_js) == str(tbg_sd):
        print("SUCCESS - loaded game matches saved")
      else:
        print("FAIL - loaded game differs from saved")
        #print(tbg_sd)
        print(tbg.serialize(True))
        print("^loaded --vs-- vfile")
        print(sd)
         
      # presume success, try things out
      print("{} is the starting player".format(tbg.currPlayer.name))

      # simulate a bunch of turns (to test game mechanics)
      print("---- simulating some game mechanics to ensure load worked ----")
      for i in range(0,40):
        tile=tbg.currPlayer.selectRandomTile()
        if tile is None:
          print("Player ran out of tiles, ending loop")
          break
        else:
          # testing both ways of playing a tile (tile object, or string)
          if i%2 == 0:
            tbg.playTile(tbg.currPlayer.getId(), alpha=str(tile))
          else:
            tbg.playTile(tbg.currPlayer.getId(), tile)
  else:
    print("no saved state")

   
   
