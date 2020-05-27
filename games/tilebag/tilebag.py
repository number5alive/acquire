from base import Game
from base import Player
from games.tilebag.player import TileBagPlayer
from games.tilebag.tiles import Tile, TileBag
from games.tilebag.board import Board
from games.tilebag.hotels import Hotel, Stock, HOTELS
from games.tilebag.gamelog import GameLog
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
  _name='TileBag'
  _minPlayers=3
  _maxPlayers=5
  _playerClass=TileBagPlayer
  _starturl='/tilebag/v1'
   
  def __init__(self, id):
    Game.__init__(self,id)
    self._initcomponents()
    self._log.recordGameMessage("Game Created")
    blah=TileBagGame.BuyStocks

  def __del__(self):
    # todo, delete all of our things
    print("Deleting TileBagGame")
    Game.__del__(self)

  def _initcomponents(self):
    StateEngine.__init__(self, TileBagGame.StartGame(self), self._checkEndCondition)
    self._conflictTiles=[]
    self.board=[]
    self._gamestate=None
    self._endcondition=False
    self._endrequested=False
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
  def currplayer(self):
    return self._currplayer

  def _getPlayer(self, playerid):
    for player in self._players:
      if player.getId() == playerid:
        return player
    return None

  # End _can be_ triggered when a hotel is > size 41, or all hotels > 11
  def _checkEndCondition(self):
    if self._started:
      bSize41=False
      bAll11=True
      bAtLeastOneHotel=False
      for h in self.hotels:
        if h.size >= 41:
          bSize41 = True
        elif h.size > 0:
          bAtLeastOneHotel = True
          if h.size < 11:
            bAll11 = False
      self._endcondition=bSize41 or (bAtLeastOneHotel and bAll11)
      if self._endcondition:
        print("END CONDITION Satisfied - Can be triggered by player")
      else:
        # cover case where an end-condition ceases to be valid
        # i.e. requested when all are size 11, then a new hotel placed
        self._endrequested = False 
      return self._endcondition
        
    return False

  # ===== External Requests into the Game Engine =====
  # These will be passed on to the state machine for handling mechanics

  def run(self):
    if not super().run():
      return False, "Unable to start the game - probably not enough players"

    return self.on_event(None, 'StartGame')

  def moneyAction(self, playerId, amount):
    errmsg="Game Hasn't Started"
    if self._started:
      player=self._getPlayer(playerId)
      if player and type(amount) is int:
        if amount > 0 or player.money >= -amount:
          player.money += amount
          self._log.recordMoneyAction(player.name, amount)
          return True, ""
        else:
          errmsg="Subtracting more than the player has"
      else:
        errmsg="Invalidly formated moneyAction request"

    return False, errmsg

  def _getHotelByName(self, hname):
    for h in self.hotels:
      if h.name == hname:
        return h
    return None

  # return or take stocks from the pile
  def stockAction(self, playerId, hotel, amount):
    player=self._getPlayer(playerId)
    h=self._getHotelByName(hotel)
    # validate args, h==None is actually okay here because we reuse this 
    #   to notify "pass" on buy stocks
    if type(amount) is not int:
      return False, "Invalidly formatted stockAction request"
       
    action=TileBagGame.EVENT_BUYSTOCKS if amount >= 0 else TileBagGame.EVENT_SELLSTOCKS
    amount=amount if amount >=0 else -amount
     
    return self.on_event(player, action, hotel=h, amount=amount)
     
  def _takeStocks(self, player, h, amount):
    if h.nstocks >= amount:
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

  # Constants to avoid typeos wreaking havoc across my code (again)
  EVENT_BUYSTOCKS='BuyStocks'
  EVENT_SELLSTOCKS='SellStocks'
  EVENT_REMOVEHOTEL='RemoveHotel'
  EVENT_PLACEHOTEL='PlaceHotel'
  EVENT_PLACETILE='PlaceTile'

  STATE_BUYSTOCKS='BuyStocks'
  STATE_STARTGAME='StartGame'
  STATE_PLACETILE='PlaceTile'
  STATE_PLACEHOTEL='PlaceHotel'
  STATE_SELECTMERGEWINNER='SelectMergeWinner'
  STATE_SELECTMERGELOSER='SelectMergeLoser'
  STATE_LIQUIDATESTOCKS='LiquidateStocks'
  STATE_ENDGAME='EndGame'

  # current player can trigger the end of the game if the end condition is set
  # NOTE: _endcondition flag is updated after every state change
  def requestEndGame(self, playerId):
    errmsg="Not the Current Player"
    player=self._getPlayer(playerId)
    if player == self._currplayer:
      if self._endcondition:
        errmsg="All Good, END REQUESTED!"
        self._endrequested=True
      else:
        errmsg="Can't trigger end state, condition not met!"
    return self._endrequested, errmsg

  # set alpha to None to remove it from the board
  # set it to a tile position to place it on the board
  def placeHotel(self, playerId, hname, alpha):
    player=self._getPlayer(playerId)
    hotel=self._getHotelByName(hname)
     
    if hotel is not None:
      if alpha is None:
        return self.on_event(player, TileBagGame.EVENT_REMOVEHOTEL, hotel=hotel)
      else:
        return self.on_event(player, TileBagGame.EVENT_PLACEHOTEL, hotel=hotel)
           
    return False, "invalid hotel, or invalid tile location"

  # REMOVE HOTEL - If it's a remove, resolve conflictTiles
  def _removeHotel(self, hotel):
    hotel.setPosition(None, occupies=None)
    self.updateConflictTiles()
    self._log.recordRemoveHotelAction(hotel.name)

  # loop through the conflict tiles and see if any are no longer in conflict
  def updateConflictTiles(self):
    for cf in self._conflictTiles:
      self.checkTileNextToHotel(cf)

  # return the spaces next to us, and a list of hotels
  def _getBorderingSpaces(self, tile):
    conn=self.board.checkNeighbours(tile.row, tile.col)
    hn=[]
    for h in self.hotels:
      if h.occupies is not None:
        # check if this space neighbours any active hotels
        tmp = [o for o in conn if o in h.occupies]
        if len(tmp) > 0:
          print("new tile at {} is adjacent to {}".format(tile, h.name))
          hn.append(h)
    return conn, hn

  def checkTileNextToHotel(self, tile):
    # find neighbouring occupied spaces
    conn, hn = self._getBorderingSpaces(tile)

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
    if tile is None:
      if alpha is not None:
        tile=Tile.newTileFromAlpha(alpha)
      else:
        return False, "Invalid argument to playTile"

    return self.on_event(self._getPlayer(playerId), 'PlaceTile', tile=tile)

  # ===== Start of the State Machine logic =====
  # note: there are a small handful of states: 
  #   playing a tile, buying stocks, placing a hotel, resolving a merger
  #   - with the last one having a few sub-states, but that's okay

  def endTurnAction(self):
    # Give player a new tile, rotate to the next player and state
    if self.tilebag.isEmpty():
      print("Tilebag exhausted, trigger end-game state")
    else:
      self._currplayer.receiveTile(self.tilebag.takeTile())
       
    # turn is over, go to EndGame state instead of the next player
    if self._endrequested:
      return True, "", TileBagGame.EndGame(self)
       
    # otherwise, give the next player their turn
    self._currplayer=next(self._rotation)
    return True, "", TileBagGame.PlaceTile(self)

  class StartGame(State):
    def toHuman(self):
      return "Waiting on game to start"

    def on_event(self, event, **kwargs):
      if event == 'StartGame':
        # Initialize Game Components
        self._game._log.recordGameMessage("TileBagGame Started!")
        self._game.board = Board(9,12)
        self._game.tilebag = TileBag(9,12)

        # Determine Start Order: draw a single tile for each player
        self._game._currplayer = None
        lowestTile=Tile(10,8)
        for player in self._game._players:
          t=self._game.tilebag.takeTile()
          self._game._log.recordTileAction(player.name, str(t))
          if t <= lowestTile:
            lowestTile=t
            self._game._currplayer=player
          self._game.board.placeTile(t)
        self._game._log.recordGameMessage("{} is the first player".format(self._game._currplayer.name))

        # Now set the game order to the above
        self._game._rotation = islice(cycle(self._game._players), self._game._players.index(self._game._currplayer)+1, None)
       
        # give each player seven tiles to start
        for player in self._game._players:
          for i in range(0,7):
            player.receiveTile(self._game.tilebag.takeTile())

        # good to go, flip into the main game state cycle
        return True, "", TileBagGame.PlaceTile(self._game)

      return False, "ILLEGAL EVENT - StartGame when not in StartGame State", self

  class PlaceTile(State):
    def toHuman(self):
      return "Waiting on {} to play a tile".format(self._game._currplayer)

    def on_event(self, event, **kwargs):
      errmsg="ILLEGAL EVENT - {} when in state PlaceTile".format(event)
      if event == 'PlaceTile':
        tile=kwargs.get('tile',None)
        if tile in self._game._currplayer.tiles:
          # check for no hotels on the board
          # or no stocks left in hotels on the board
          bHotelsOnBoard=False
          bAllHotelsOnBoard=True
          bStocksAvailable=False
          ofSize11=0
          conn, hn = self._game._getBorderingSpaces(tile)
          for h in self._game.hotels:
            if h.size > 0:
              bHotelsOnBoard=True
              if h.nstocks > 0:
                bStocksAvailable=True
              if h in hn and h.size >= 11:
                ofSize11+=1
            else:
              bAllHotelsOnBoard=False
              
          # Check for illegal move (borders two hotels of size 11, or
          #       All hotels on the board and this would make another)
          bWouldMakeNewHotel=len(conn) > 0 and len(hn) == 0
          if (ofSize11 >= 2) or (bAllHotelsOnBoard and bWouldMakeNewHotel):
            return False, "ERROR - Illegal Tile Move", self
           
          # NOTE: this tile MIGHT be between two tiles, in that case we need
          #       to ensure it doesn't cause a "merger" until one of those
          #       hotels gets removed, therefore:
           
          # put tile on the board, and presume it'll be between two tiles
          # now verify that fact for this tile, cleanup if we were wrong
          self._game.board.placeTile(tile)
          self._game._conflictTiles.append(tile)
          self._game.checkTileNextToHotel(tile)
          self._game._log.recordTileAction(self._game._currplayer.name, str(tile))
          self._game._currplayer.removeTile(tile)
          print("Played Tile: {}".format(tile))
           
          if len(self._game._conflictTiles) > 0:
            return True, "", self._game._resolveMerger(self._game, tile)
           
          # more than one tile borders, and none are hotels, New Hotel!
          if bWouldMakeNewHotel:
            return True, "", TileBagGame.PlaceHotel(self._game, tile)
           
          # If there's no stocks to buy, skip to next person
          if not bStocksAvailable:
            return self._game.endTurnAction()
             
          # Default after playing a tile is to buy stocks
          return True, "", TileBagGame.BuyStocks(self._game)
        else:
          errmsg="{} is not in {}".format(tile, self._game._currplayer.tiles)

      # if we get down here, we didn't succeed at playing the tile
      return False, errmsg, self

  class PlaceHotel(State):
    def __init__(self, game, tile):
      self._game=game
      self._tile=tile
      self._alpha=str(tile)
 
    def toHuman(self):
      return "Waiting on {} to place a Hotel".format(self._game._currplayer)

    def serialize(self, forsave=False):
      validhotels=[]
      for h in self._game.hotels:
        if h.size == 0:
          validhotels.append(h.name)
           
      return { 'validhotels': validhotels }

    def on_event(self, event, **kwargs):
      errmsg="ILLEGAL EVENT - {} when in state PlaceHotel".format(event)
      if event == TileBagGame.EVENT_PLACEHOTEL:
        if 'hotel' in kwargs:
          hotel=kwargs['hotel']
          if hotel.tile is None:
            conn = self._game.board.findConnected(None, self._tile.row, self._tile.col, skip=self._game._conflictTiles)
            hotel.setPosition(self._alpha, occupies=conn)
            self._game._takeStocks(self._game._currplayer, hotel, 1)
            self._game._log.recordPlaceHotelAction(hotel.name, self._alpha)
            return True, "", TileBagGame.BuyStocks(self._game)
          else:
            errmsg="Hotel is already on the board!"
        else:
          errmsg="invalid arguments to PlaceTile event"
      else:
        errmsg="Invalid event {} while waiting for hotel to be placed".format(event)
      return False, errmsg, self
       
  class BuyStocks(State):
    def __init__(self, game):
      self._game=game
      self._bought=0
      print(self.toHuman())

    def toHuman(self):
      return "Waiting on {} to Buy Stocks".format(self._game._currplayer)

    def serialize(self, forsave=False):
      return { 'canbuy' : 3 - self._bought }
       
    def on_event(self, event, **kwargs):
      errmsg="ILLEGAL EVENT - {} when in state BuyStocks".format(event)
      if event == TileBagGame.EVENT_BUYSTOCKS:
        if 'amount' in kwargs:
          amount=kwargs['amount']
          hotel=kwargs.get('hotel', None)
          player=self._game._currplayer
          if amount == 0:
            # player is signalling the end of their turn
            return self._game.endTurnAction()
          elif hotel is not None and amount > 0 and hotel.price() is not None:
            # player is attempting to buy some stock, make sure it's a legal amount
            if self._bought + amount <= 3:
              # calculate how much and make sure player has that amount
              cost=hotel.price() * amount
              if player.money >= cost:
                if self._game._takeStocks(player, hotel, amount):
                  self._bought += amount
                  player.money -= cost
                  self._game._log.recordStockAction(player.name, hotel.name, amount, -cost)
                  if self._bought == 3:
                    return self._game.endTurnAction()
                     
                  return True, "", self
                else:
                  errmsg="Not enough stocks left to complete this transaction"
              else:
                errmsg="not enough money to complete transaction. cost={}*{}={}".format(hotel.price(), amount, cost)
            else:
              errmsg="trying to buy too many stocks on your turn"
          else:
            errmsg="invalid arguments. Is the hotel on the board?!"
        else:
          errmsg="invalid arguments in BuyStocks event"
         
      return False, errmsg, self

  # NOTE: Not a class, a factory method to determine which state to land in
  def _resolveMerger(self, game, tile, biggest=None, smallest=None):
    conn, merging=game._getBorderingSpaces(tile)
    merging.sort(key=lambda x: x.size, reverse=True)

    # Check for exit condition (all mergers completed)
    # current player gets to do their buy stock action
    if len(merging) == 1:
      return TileBagGame.BuyStocks(game)

    # WARNING: Complicated logic here... 
    # buy out from smallest to biggest, but we have to be careful...
    # there may be multiple smallests or biggests
    # When merger is triggered, all states need to call back to this function
    # so we can  resolve them in order

    if biggest is None and merging[0].size == merging[1].size:
      print("more than one are biggest")
      bigoption=[h for h in merging if h.size == merging[0].size]
      return TileBagGame.SelectMergeWinner(game, tile, bigoption)
       
    biggest=biggest if biggest is not None else merging[0]
    merging.remove(biggest) # pull biggest out of the list

    if smallest is None and len(merging) >=2 and merging[-1].size == merging[-2].size:
      print("more than one are the smallest")
      smalloption=[h for h in merging if h.size == merging[1].size]
      return TileBagGame.SelectMergeLoser(game, tile, biggest, smalloption)
       
    smallest=smallest if smallest is not None else merging[-1]
    print("We know {} ({}) is bigger than {} ({})".format(biggest.name, biggest.size, smallest.name, smallest.size))
    return TileBagGame.LiquidateStocks(game, tile, biggest, smallest)
      
  class SelectMergeWinner(State):
    def __init__(self, game, tile, bigoption):
      self._game=game
      self._tile=tile
      self._bigoption=bigoption
      print(self.toHuman())

    def toHuman(self):
      return "Waiting for {} to select the hotel that will acquire the others - between:{}".format(self._game._currplayer, [h.name for h in self._bigoption])

    def serialize(self, forsave=False):
      return { 'bigoption' : [h.name for h in self._bigoption], }

    def on_event(self, event, **kwargs):
      errmsg="ILLEGAL EVENT - {} when in state SelectMergeWinner".format(event)
      if event == TileBagGame.EVENT_PLACEHOTEL:
        hotel=kwargs.get('hotel', None)
        if hotel in self._bigoption:
          return True, "", self._game._resolveMerger(self._game, self._tile, biggest=hotel)
        else:
          errmsg="Must select hotel in the list {}".format([h.name for h in self._bigoption])
      return False, errmsg, self
       
  class SelectMergeLoser(State):
    def __init__(self, game, tile, biggest, smalloption):
      self._game=game
      self._tile=tile
      self._biggest=biggest
      self._smalloption=smalloption
      print(self.toHuman())

    def toHuman(self):
      return "Waiting for {} to select the hotel that will BE acquired by {} - between:{}".format(self._game._currplayer, self._biggest.name, [h.name for h in self._smalloption])

    def serialize(self, forsave=False):
      return { 'smalloption' : [h.name for h in self._smalloption], }

    def on_event(self, event, **kwargs):
      errmsg="ILLEGAL EVENT - {} when in state SelectMergeLoser".format(event)
      if event == TileBagGame.EVENT_REMOVEHOTEL:
        hotel=kwargs.get('hotel', None)
        if hotel in self._smalloption:
          return True, "", self._game._resolveMerger(self._game, self._tile, biggest=self._biggest, smallest=hotel)
        else:
          errmsg="Must select hotel in the list {}".format([h.name for h in self._smalloption])
      return False, errmsg, self

  # pays out majority and minority shareholders
  # used by both LiquidateStocks and EndGame states
  def _payoutBonuses(self, hotel, liquidate=False):
    shareholders=[{'stocks' : p.numStocks(hotel.name), 'player':p,} for p in self._players]
    shareholders.sort(key=lambda x: x['stocks'], reverse=True)

    self._log.recordGameMessage("Resolving Takeover of {} - shareholders: {}".format(hotel.name, ["{}={} ".format(sh['player'], sh['stocks']) for sh in shareholders]))

    majsh=[p for p in shareholders if p['stocks'] == shareholders[0]['stocks']]
    minsh=[p for p in shareholders if p['stocks'] == (shareholders[1]['stocks'] if shareholders[1]['stocks'] > 0 else shareholders[0]['stocks'])]
    print("Majority Shareholders: {}".format(majsh))
    print("Minority Shareholders: {}".format(minsh))
     
    majb, minb = hotel.bonuses()
    majsplit=majb//len(majsh)//100*100
    minsplit=minb//len(minsh)//100*100
     
    # give the players their money, record the transaction
    for p in majsh:
      player=p['player']
      player.money += majb
      self._log.recordBonusPayout(player, 'majority', majb)
    for p in minsh:
      player=p['player']
      player.money += minb
      self._log.recordBonusPayout(player, 'minority', minb)
    return { 'hotel' : hotel.name,
             'majority': {'amount': majb,
                          'splits': majsplit,
                          'players': majsh},
             'minority': {'amount': minb,
                          'splits': minsplit,
                          'players': minsh},
             'shareholders': shareholders,
            }

  class LiquidateStocks(State):
    def __init__(self, game, tile, biggest, smallest):
      self._game=game
      self._tile=tile
      self._biggest=biggest
      self._smallest=smallest
      self._startplayer=self._game._currplayer
      print(self.toHuman())
      self._game._log.recordMerger(self._biggest.name, self._smallest.name)
       
      # find out maj/min shareholder bonus'
      self._bonuses=self._game._payoutBonuses(self._smallest)

      # rotate forward through to a player with shares in the smallest
      # this is safe enough, *someone* has a stock, the free one 
      while self._checkPlayerDone():
        print("finding first player with stocks in {}".format(self._smallest))
        self._game._currplayer=next(self._game._rotation)
       
    def toHuman(self):
      return "Waiting for {} to pick stock options".format(self._biggest.name, self._smallest.name, self._game._currplayer, self._smallest.name)

    def serialize(self, forsave=False):
      return { 'bonuses': self._bonuses,
               'biggest': self._biggest.name,
               'smallest': self._smallest.name, }
       
    # loop through to the next player with stocks in smallest, 
    def _onPlayerDone(self):
      self._game._currplayer=next(self._game._rotation)
      while self._game.currplayer != self._startplayer:
        if not self._checkPlayerDone():
          return self
        self._game._currplayer=next(self._game._rotation)
       
      # That's all she wrote... Take the smallest hotel out of the equation
      # Note: if we don't do this we'll have a beautiful endless loop
      self._game._removeHotel(self._smallest)
      return self._game._resolveMerger(self._game, self._tile, biggest=self._biggest)

    # helper, check if no stocks in smallest hotel, obviously done then
    def _checkPlayerDone(self):
      return self._game.currplayer.numStocks(self._smallest.name) == 0
       
    def on_event(self, event, **kwargs):
      # Buy > 0(Bigger) - trigger 2-for-1
      # Sell > 0 (Smaller) - sell
      # Buy == 0 (Bigger or Smaller) - End
       
      # just a shorter form since we use this a lot
      player=self._game.currplayer
       
      errmsg="ILLEGAL EVENT - {} when in state LiquidateStocks".format(event)
      if event == TileBagGame.EVENT_BUYSTOCKS:
        if 'amount' in kwargs:
          amount=kwargs['amount']
          hotel=kwargs.get('hotel', None)
           
          # Check if player is signalling the end of their turn
          if amount == 0:
            remStocks = player.numStocks(hname=self._smallest.name)
            if remStocks >= 0:
              self._game._log.recordGameMessage("{} is keeping {} stocks in {}".format(self._game._currplayer.name, remStocks, self._smallest.name))
            return True, "", self._onPlayerDone()
            
          # Check 2-for-1
          if hotel is self._biggest:
            # make sure the big hotel has enough stocks
            if hotel.nstocks >= amount:
              # make sure the player has 2*amount of smallest stocks
              nSmallest=player.numStocks(hname=self._smallest.name)
              if nSmallest >= 2*amount:
                self._game._returnStocks(player, self._smallest, 2*amount)
                self._game._takeStocks(player, self._biggest, amount)
                self._game._log.recordStockTrade(player.name, self._smallest.name, self._biggest.name, amount)
                
                # make the 2-for-1 swap
                return True, "", self if not self._checkPlayerDone() else self._onPlayerDone()
              else:
                errmsg="Player doesn't have enough stocks for swap {}".format(nSmallest)
            else:
              errmsg="Big hotel doesn't have enough stocks: {}".format(hotel.nstocks)
          else:
            errmsg="Invalid Buy action in Liquidate - can only be for biggest hotel: {}".format(self._biggest)
        else:
          errmsg="Invalid args to Liquidate Stock Event (buy/keep)"
      elif event == TileBagGame.EVENT_SELLSTOCKS:
        if 'amount' in kwargs:
          amount=kwargs['amount']
          hotel=kwargs.get('hotel', None)
           
          if amount > 0 and hotel is self._smallest:
            # make sure the player has amount of smallest, sell them
            if self._game._returnStocks(player, hotel, amount):
              value=hotel.price()*amount
              player.money += value
              self._game._log.recordStockAction(player.name, hotel.name, -amount, value)
              return True, "", self if not self._checkPlayerDone() else self._onPlayerDone()
            else:
              errmsg="player doesn't have {} stocks to sell".format(amount)
          else:
            errmsg="Sell action has to be >0 ({}) and for {} ({})".format(amount, self._smallest.name, hotel)
        else:
          errmsg="Invalid args to Liquidate Stock Event (sell)"
          
      return False, errmsg, self

  class EndGame(State):
    def __init__(self, game):
      self._game=game
      self._bonuses=[]
      self._buyouts=[]
       
      blah=sorted(self._game.hotels, key=lambda x: x.size, reverse=False)
      for h in blah:
        if h.size > 0:
          print("Resolving {}, size {}".format(h.name, h.size))
          self._bonuses.append(self._game._payoutBonuses(h))
          for p in self._game._players:
            amount=p.numStocks(hname=h.name)
            print("{} has {} stocks in {}", p.name, amount, h.name)
            if amount > 0:
              self._game._returnStocks(p, h, amount)
              value=h.price()*amount
              p.money += value
              self._game._log.recordStockAction(p.name, h.name, -amount, value)
              #TODO: add the value of amount sold to this list
              # the code below borks, because of how we return payout information in _payoutBonuses above
              #self._payouts[h.name][p.name]={'amount':amount, 'value':value}

      blah=sorted(self._game._players, key=lambda x: x.money, reverse=True)
      self._game._log.recordGameMessage("Final Totals")
      for p in blah:
        self._game._log.recordGameMessage("{}: ${:0,.2f}".format(p.name, p.money))

    def toHuman(self):
      return "End State! Cashing out the remaining hotels on the board"

    def serialize(self, forsave=False):
      return { 
          'finalscores': [{'name':p.name,'amount':p.money} for p in self._game._players],
          'bonuses': self._bonuses,
          }

    def on_event(self, event, **kwargs):
      return False, "EndState doesn't handle any events, you're here for the long haul mister!", self

  # ===== Serialization and Deserialization of the Game object ====
  # both for the clients, as well as for saving and restoring state

  # Load (recreate) a version of this game from the JSON object
  def loadFromSavedData(self,sd):
    gd=sd['gamedata']
     
    # create the players
    for player in sd['players']:
      p=TileBagPlayer.loadFromSavedData(player)
      self.addPlayer(p)

    # restore the board and the tilebag
    self.board=Board.loadFromSavedData(gd['board'])
    rows, cols =self.board.getBoardSize()
    self.tilebag=TileBag(rows, cols, initialTiles=gd['bag'])

    # restore the hotels
    self.hotels=[]
    for hotel in gd['hotels']:
      self.hotels.append(Hotel.loadFromSavedData(hotel))
       
    # restore the game state
    self._started=sd['started']
     
    # lookup dictionary to convert string into the State class
    # mainly required for "save" save/restore functionality from json
    lookup_state = { 
      TileBagGame.STATE_BUYSTOCKS : TileBagGame.BuyStocks,
      TileBagGame.STATE_STARTGAME : TileBagGame.StartGame,
      TileBagGame.STATE_PLACETILE : TileBagGame.PlaceTile,
      TileBagGame.STATE_PLACEHOTEL : TileBagGame.PlaceHotel,
      TileBagGame.STATE_SELECTMERGEWINNER : TileBagGame.SelectMergeWinner,
      TileBagGame.STATE_SELECTMERGELOSER: TileBagGame.SelectMergeLoser,
      TileBagGame.STATE_LIQUIDATESTOCKS: TileBagGame.LiquidateStocks,
      TileBagGame.STATE_ENDGAME: TileBagGame.EndGame,
      }
   
    # restore the state machine
    sm=gd['gamestate']
    self._currplayer=self._getPlayer(sm['currplayer']['id'])
    self._rotation = islice(cycle(self._players), self._players.index(self._currplayer)+1, None)
    stateclass=lookup_state[sm['state']]
    print("creating state class: {}".format(stateclass))
    if len(sm['stateinfo']) == 0:
      self._state=stateclass(self)
    else:
      self._state=stateclass(self, **sm['stateinfo'])

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
        'gamestate': StateEngine.serialize(self, True),
        'board': self.board.serialize(),
        'bag': self.tilebag.serialize(),
        'hotels': [h.serialize(forsave=True) for h in self.hotels],
        'gamelog': self._log.serialize(),
      }
    else:
      return {}

  # Get the information you'd see if you were looking at this game on a table
  def getPublicInformation(self):
    if self._started:
      return {
        'gamestate': StateEngine.serialize(self, False),
        'endpossible': self._endcondition,
        'endrequested': self._endrequested,
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
  print("{} is the starting player".format(tbg.currplayer.name))

  # simulate a bunch of turns
  for i in range(0,40):
    print("{} tiles: {}".format(tbg.currplayer.name, tbg.currplayer.tiles))
    tile=tbg.currplayer.selectRandomTile()
    tbg.playTile(tbg.currplayer.getId(), tile)
   
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
  
