from base import Game
from base import Player
from games.tilebag.player import TileBagPlayer
from games.tilebag.tiles import Tile, TileBag
from games.tilebag.board import Board
from games.tilebag.hotels import Hotel, Stock, HOTELS
from games.tilebag.gamelog import GameLog, GameAction
from games.tilebag.stateengine import State, StateEngine
from itertools import cycle, islice

class TileBagGame(Game, StateEngine):
  """
  THIS... this is the game... It has all the logic and state for a game of
  TileBag. You'll notice it inherits both the base Game class (so it can run
  on this framework), and StateEngine - because I'm switching it over to run
  as discrete game states via a state machine... why not, every other 
  decision has basically been this random!
  """
  # Fixed Data about the Game
  _STATES={'placetile': 'place a tile', 
           'placehotel': 'place a hotel', 
           'buystocks': 'buy stocks',
           'picktakeover': 'pick hotel to be acquired',
           'resovlestocks': 'resolve acquired stocks' }
            
  _name='TileBag'
  _minPlayers=3
  _maxPlayers=5
  _playerClass=TileBagPlayer
  _starturl='/tilebag/v1'
   
  def __init__(self, id):
    Game.__init__(self,id)
    self._initcomponents()
    self._log.recordGameMessage("Game Created")

  def __del__(self):
    # todo, delete all of our things
    print("Deleting TileBagGame")
    Game.__del__(self)

  def _initcomponents(self):
    self._conflictTiles=[]
    self.board=[]
    self._currPlayer=None
    self._gamestate=None
    self.tilebag=None;
    self.hotels=[Hotel(h['name'], h['chart']) for h in HOTELS]
    self._log=GameLog()

  def reset(self):
    self._log.recordGameMessage("Resetting TileBag")
    del self._conflictTiles
    del self.board
    del self.hotels
    del self.tilebag
    del self._log
    self._initcomponents()
    for player in self._players:
      player.reset()
       
    # only thing from base class to reset is the "started" flag
    Game.reset(self)

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

  # ===== External Requests into the Game Engine =====
  # These will be passed on to the state machine for handling mechanics

  def run(self):
    if not super().run():
      print("Unable to start the game - probably not enough players")
      return False;
       
    # Initialize Game Components
    self._log.recordGameMessage("TileBagGame Started!")
    self.board = Board(9,12)
    self.tilebag = TileBag(9,12)

    # Determine Start Order: draw a single tile for each player
    self._gamestate='placetile'
    self._currPlayer = None
    lowestTile=Tile(10,8)
    for player in self._players:
      t=self.tilebag.takeTile()
      self._log.recordTileAction(player.name, str(t))
      if t <= lowestTile:
        lowestTile=t
        self._currPlayer=player
      self.board.placeTile(t)
    self._log.recordGameMessage("{} is the first player".format(self._currPlayer.name))

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
          self._log.recordMoneyAction(player.name, amount)
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
      self._log.recordStockAction(player.name, h.name, amount)
      return True
    return False
       
  def _returnStocks(self, player, h, amount):
    if player.numStocks(hname=h.name) >= amount:
      for i in range(0,amount):
        s=player.returnStock(h.name)
        if not h.returnStock(s):
          return False
      self._log.recordStockAction(player.name, h.name, -amount)
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

          self._log.recordRemoveHotelAction(h.name)
           
          return True
        
        # ADD HOTEL - if it's an add, determine what spaces it occupies
        elif self.board.alphaIsValid(alpha):
          # find the full list of connected tiles
          r, c = Tile.fromAlpha(alpha)
          conn = self.board.findConnected(None, r, c, skip=self._conflictTiles)
          print("Connected to {} is: {}".format(alpha, conn))
           
          # TODO: make sure there are at least two connected tiles
          h.setPosition(alpha, occupies=conn)
          self._log.recordPlaceHotelAction(h.name, alpha)
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

          self._log.recordTileAction(self._currPlayer.name, str(tile))

          # TODO: Change the game state to either:
          # makeHotel, resolveMerger, buyStocks, 

          # TODO: Move this to the "end turn" action
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

  # ===== Start of the State Machine logic =====
  # note: there are a small handful of states: 
  #   playing a tile, buying stocks, placing a hotel, resolving a merger
  #   - with the last one having a few sub-states, but that's okay

  class StartGame(State):
    def on_event(self, event, **kwargs):
      return self

    def toHuman(self):
      return "Waiting on game to start"

  class PlayTile(State):
    def on_event(self, event, **kwargs):
      # see if there's a new hotel to go down
      # see if there's a merger about to happen
      return self

    def toHuman(self):
      return "Waiting on {} to play a tile".format(self._game._currplayer)

  class PlaceHotel(State):
    def on_event(self, event, **kwargs):
      return self

  class BuyStocks(State):
    def on_event(self, event, **kwargs):
      return self

  class ResolveMerger(State):
    def on_event(self, event, **kwargs):
      return self

  class LiquidateStocks(State):
    def on_event(self, event, **kwargs):
      return self

  # ===== Serialization and Deserialization of the Game object ====
  # both for the clients, as well as for saving and restoring state

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

  def getPlayerInfo(self, playerid):
    player=self._getPlayer(playerid)
    if player:
      return player.serialize(True)
    return None
   
  # Saves the game to json format (using the JSONEncoder from elsewhere)
  # Why is this different than getPublicInformation? Because I'm super lazy!
  # TODO: find a cute way to merge these
  def saveGameData(self):
    if self._started:
      return { 
        'currPlayer': self._currPlayer.getId(),
        'gamestate': self._gamestate,
        'board': self.board.serialize(),
        'bag': self.tilebag.serialize(),
        'hotels': [h.serialize() for h in self.hotels]
      }
    else:
      return {}

  def convertStateToHuman(self):
     return "Waiting for {} to {}".format(self._currPlayer.name, TileBagGame._STATES[self._gamestate])
      
  # Get the information you'd see if you were looking at this game on a table
  def getPublicInformation(self):
    if self._started:
      return {
        'currPlayer': self._currPlayer.serialize(False),
        'gamestate': self.convertStateToHuman(),
        'board': self.board.serialize(),
        'players' : [x.serialize(False) for x in self._players],
        'hotels': [h.serialize() for h in self.hotels],
        'gamelog': self._log.serialize(last=10),
      }
    else:
      return {}

if __name__ == "__main__":
  print("name: " + TileBagGame.name())
  print("min: " + str(TileBagGame.minPlayers()))
  print("max: " + str(TileBagGame.maxPlayers()))
  print("fullname: " + TileBagGame.fullname())

  # Initialize a new game, with three players, and start it
  tbg=TileBagGame(1)
  p=TileBagPlayer(100, "Stan", money=7000)
  tbg.addPlayer(p)
  tbg.addPlayer(tbg.newPlayer(1))
  tbg.addPlayer(tbg.newPlayer(2))
  tbg.addPlayer(tbg.newPlayer(3))
  tbg.run()

  currBoard = tbg.getBoard()
  print("{} is the starting player".format(tbg.currPlayer.name))

  # simulate a bunch of turns
  for i in range(0,40):
    print("{} tiles: {}".format(tbg.currPlayer.name, tbg.currPlayer.tiles))
    tile=tbg.currPlayer.selectRandomTile()
    tbg.playTile(tbg.currPlayer.getId(), tile)
   
  # stress the serialization functions
  print(">>> getPublicInformation: {}".format(tbg.getPublicInformation()))
  print(">>> saveGameData: {}".format(tbg.saveGameData()))
  print(">>> serialize: {}".format(tbg.serialize(True)))

  print("---- Testing the hotel movement functionality ----")
  print("Adding hotel: {}".format(tbg.placeHotel(1,"American","1A")))
  print("Adding hotel: {}".format(tbg.placeHotel(1,"Tower","2B")))
  print("Invalid hotel position: {}".format(not tbg.placeHotel(1,"Tower","B2")))
  print("Invalid hotel: {}".format(not tbg.placeHotel(1,"Arbuckle","7B")))
  print("Removing hotel: {}".format(tbg.placeHotel(1,"American",None)))
  print(">>> getPublicInformation: {}".format(tbg.getPublicInformation()))

  print("---- Testing the stock mechanics -----")
  print("Taking stock: {}".format(tbg.stockAction(100,"American",3)))
  print("Taking stock: {}".format(tbg.stockAction(100,"Tower",1)))
  print("Taking stock: {}".format(tbg.stockAction(100,"Continental",5)))
  print("Invalid stock: {}".format(not tbg.stockAction(100,"Arbuckle",1)))
  print("Invalid amount: {}".format(not tbg.stockAction(100,"American","a")))
  print("Returning stock: {}".format(tbg.stockAction(100,"American",-2)))
  print("Returning invalid amount: {}".format(not tbg.stockAction(100,"Saxxon",-2)))
  print(">>> getPublicInformation: {}".format(tbg.getPublicInformation()))

  print("---- Testing TileBagPlayer money functionality ----")
  print("valid + Money: {}".format(tbg.moneyAction(100, 100)))
  print("valid - Money: {}".format(tbg.moneyAction(100, -200)))
  print("invalid Money: {}".format(not tbg.moneyAction(100, "$10" )))
  print("too much - Money: {}".format(not tbg.moneyAction(100, -100000 )))

  print("savePlayerData: {}".format(p.savePlayerData()))
   
  print("---- Testing TileBagGame reset functionality ----")
  print(">>> saveGameData: {}".format(tbg.saveGameData()))
  tbg.reset()
  tbg.run()
  print(">>> saveGameData: {}".format(tbg.saveGameData()))
  
