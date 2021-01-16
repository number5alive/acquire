import sys #handling command line parameters
import json #well, everything is json nowadays, isn't it?
import socketio #to be notified of game state changes
import requests #for GET/POST/PATCH http requests into the REST endpoints
import games.tilebag.aiplayer.constants as constants #for constants
from time import sleep #to optinonally simulate the human speed of play
import random #picking tiles at random for now
import threading #so we can still do other stuff while this player runs!
from ai.tilebag.tbREST import TileBagREST #to make the calls over to the REST Engine
from ai.tilebag.aiplayer_base import TileBagBASEAIPlayer

class AggressiveTileBagAIPlayer(TileBagBASEAIPlayer):
  ''' An Aggressive Automata that can play TileBag - shamelessly stolen from Fred's code and adapted 
       - uses the new websocket messages that are available: yourturn, privateinfo, publicinfo 
       - uses the new TileBagREST helper class to tidy things up a bit
      '''
       
  def __init__(self, gameserver="http://localhost:5000", gameid="test", playerid="513"):
    self.style = "aggressive"
    self.unplayableTiles=[] #list to store tiles in our hand we've tried to play previously, wihout success
    super().__init__(gameserver=gameserver, gameid=gameid, playerid=playerid)
    if constants.LOGLEVEL>=1: print("Aggressive TileBag Automata Created")

  def turnHandler(self):
    ''' The brains of this automata, handles indications of state change '''
    print("in turnHandler")

    # we only take an action if it's our turn
    # ... we shouldn't really get here othewise, but worth it to check
    if self.currplayer == self.playerid:
      if self.gameinfo['game']['endpossible'] == True and not self.gameinfo['game']['endrequested'] == True and self.considerEnding():
        print("used this action to trigger end game - we'll get called again!")
      elif self.currstate == "PlaceTile": self.placeTile()
      elif self.currstate == "PlaceHotel": self.placeHotel() 
      elif self.currstate == "BuyStocks": self.buyStock()
      elif self.currstate == "TradeStock": self.tradeStock()
      elif self.currstate == "SelectMergeLoser": self.selectMergeLoser()
      elif self.currstate == "SelectMergeWinner": self.selectMergeWinner()
      elif self.currstate == "LiquidateStocks": self.liquidateStocks()
      elif self.currstate == "EndGame": self.gameOver()

  def placeTile(self):
    ''' pick tiles at random from our rack '''
    #the server will reject illegal moves, so try at random until it works
    if constants.LOGLEVEL>=3: print("tile hand: {}".format(self.myinfo['tiles']))
    randomTileList = [tile for tile in self.myinfo['tiles']]
     
    while True:
      random.shuffle(randomTileList)

      if len(randomTileList)>0:
        tile = randomTileList.pop()
   
        if constants.LOGLEVEL>=1: print("we think we'll play this tile %s" % tile)
        rc, data = self.tb.placeTile(tile)
        if rc != 200: 
          print("ERROR - placing tile {} was rejected: {}".format(tile, data))
        else:
          return
           
    print("?!?! there are no (playable?) tiles in our hand!?")
    self.killAILoop()

  #this is where we place the hotel for which we have remaining stock and/or the most expensive stock
  def placeHotel(self):
    #find the most expensive hotel left (we shouldn't reach this code if there are no hotels left to place)
    #the datastructure is already ordered from cheapest to most expensive, so popping the last hotel from the list without a price
    hotel=list(iter(item for item in self.gameinfo['game']['hotels'] if item['price'] is None))[-1].get("name")
    
    if constants.LOGLEVEL>=1: print("we think we'll launch this %s chain; it's worth the most" % hotel)
    rc, data = self.tb.placeHotel(hotel, "lastplaced")
    if rc != 200: 
      print("ERROR - illegal move trying to place a hotel\n%s" % data)

  #this is where the AI will also hopefully shine
  def buyStock(self):
    #let's buy the best stock we can afford (stock available and hotel on the board) if we have enough money
    money = self.myinfo['money']
    canbuy = self.gameinfo['game']['gamestate']['stateinfo']['canbuy']

    # (smartly) try to buy stocks until it succeeds
    # when we pick 0 randomly it'll be the "no stock" action, so this will succeed eventually
    while True:
      # randomly select hotel and stocks to buy
      numtobuy=random.randint(0,canbuy)
      htobuy=random.choice([item for item in self.gameinfo['game']['hotels'] if item['price'] is not None])

      # this is the "smartly" part (unless buying zero, make sure we have the ca$h or pick again)
      if numtobuy != 0 and (htobuy['price']*numtobuy > money or htobuy['stocks']<numtobuy):
        continue
      
      # make the request to the server
      rc, data = self.tb.buyStocks(htobuy['name'], numtobuy)
      # if it succeeds we're in business, if not (somewhat expected), that's okay
      if rc != 200:
        print("illegal move trying to buy stock!\n%s" % data)
      else:
        break # needed so we only do one BuyStocks action per turn (otherwise we'll get out of sync)
    return

  #simple logic here
  def selectMergeLoser(self):
    mergeOptionsList = self.gameinfo['game']['gamestate']['stateinfo']['smalloption']
    if constants.LOGLEVEL>=1: print("we must consider which chain will survive between %s" % mergeOptionsList)
    holdings = self.myinfo['stocks']
    hotels = self.gameinfo['game']['hotels']

    #extract the relevant fields and add holdings from the hotels dictionary list for hotels we own stock in 
    myHotels = [dict({key: hotel[key] for key in ('name', 'stocks','majority','minority')},
      **{'ownstocks':holdings.get(hotel['name'])}) for hotel in hotels if hotel['name'] in [*holdings] and hotel['name'] in mergeOptionsList]
    if constants.LOGLEVEL>=2: print("holdings: %s" % holdings)
    if constants.LOGLEVEL>=2: print("hotels: %s" % hotels)
    if constants.LOGLEVEL>=2: print("myHotels: %s" % myHotels)

    #improvement => compute value table and pick best
    
    #do we have majority in any chain?
    #convert these into probability assessments
    if len(myHotels) > 0:
      if [hotel for hotel in myHotels if hotel['ownstocks']>(constants.NUMSTOCKS-hotel['stocks'])/2]:
        #pick the one with the biggest bonus

        hotelName = sorted(iter(hotel for hotel in myHotels if hotel['ownstocks']>(constants.NUMSTOCKS-hotel['stocks'])/2),
          key= lambda i:i['majority'])[0]['name']
        if constants.LOGLEVEL>=1: print("we have majority for %s; let's collapse it" % hotelName)
      #do we have minority in any chain?
      elif [hotel for hotel in myHotels if hotel['ownstocks']>(constants.NUMSTOCKS-hotel['stocks'])/len(self.gameinfo['game']['players'])]:
        hotelName = sorted(iter(hotel for hotel in myHotels if hotel['ownstocks']>
          (constants.NUMSTOCKS-hotel['stocks'])/len(self.gameinfo['game']['players'])),
          key= lambda i:i['minority'])[0]['name']
        if constants.LOGLEVEL>=1: print("we have at least minority for %s; let's collapse it" % hotelName)
      else:
        #we wish to trade some stocks 2:1, so pick the chain for which we have the fewest stocks
        hotelName = sorted(iter(hotel for hotel in myHotels),key= lambda i:i['ownstocks'])[0]['name']
        if constants.LOGLEVEL>=1: print("trading up our stocks by collapsing %s" % hotelName)
    #doesn't matter let's pick at random
    else:
      hotelName = random.choice(mergeOptionsList)

    if constants.LOGLEVEL>=1: print("we've selected to collapse %s" % hotelName)
    rc, data = self.tb.placeHotel(hotelName, None)
    if rc != 200:
      print("ERROR - illegal move trying to remove a hotel\n%s" % data)
    
  def selectMergeWinner(self):
    mergeOptionsList = self.gameinfo['game']['gamestate']['stateinfo']['bigoption']
    if constants.LOGLEVEL>=1: print("we must consider which chain will survive between %s" % mergeOptionsList)
    holdings = self.myinfo['stocks']
    hotels = self.gameinfo['game']['hotels']

    #extract the relevant fields and add own stocks and total worth from the hotels dictionary list for hotels in mergeOptionsList 
    myHotels = [dict({key: hotel[key] for key in ('name', 'stocks','price')},
            **{'ownstocks':int(holdings.get(hotel['name']) or 0)},
            **{'ownworth':int(holdings.get(hotel['name']) or 0)*int(hotel['price'] or 0)}) #clever trick to null out when there you own no stock
              for hotel in hotels if hotel['name'] in mergeOptionsList]
      
    if constants.LOGLEVEL>=2: print("holdings: %s" % holdings)
    if constants.LOGLEVEL>=2: print("hotels: %s" % hotels)
    if constants.LOGLEVEL>=2: print("myHotels: %s" % myHotels)

    #find chain worth the most by sorting list on ownworth and takin the last entry
    selectedHotel=sorted(myHotels, key=lambda x: x['ownworth'])[-1]
    if constants.LOGLEVEL>=1: print("we think we'll retain this %s chain; it's worth the most (%s)" % 
        (selectedHotel['name'],selectedHotel['ownworth']))
    rc, data = self.tb.placeHotel(selectedHotel['name'], "lastplaced")
    if rc != 200: 
      print("ERROR - illegal move trying to place a hotel to merge\n%s" % data)


  #will use simple logic here
  def liquidateStocks(self):
    #we don't need to handle the case of multiple hotel chains collapsing
    #(game server will request player's action for each in separate round robin turns)
    
    smallestChain = self.gameinfo['game']['gamestate']['stateinfo']['smallest']
    biggestChain = self.gameinfo['game']['gamestate']['stateinfo']['biggest'] #for stocks purchase orders
    holdings = self.myinfo['stocks']
    if constants.LOGLEVEL>=2: print("we must trade, sell and/or hold stock from %s (%i units) into %s (%i units)" % (smallestChain, holdings[smallestChain], biggestChain, holdings[biggestChain] if biggestChain in holdings else 0))

    #are there stock left to buy?
    biggestHotelStocks=next(hotel for hotel in self.gameinfo['game']['hotels'] if hotel['name']==biggestChain)['stocks']
    if constants.LOGLEVEL>=2: print("holdings: %s" % holdings)
    if constants.LOGLEVEL>=2: print("biggestHotelStocks left to buy: %s" % biggestHotelStocks)

    #no need to loop, the server will keep 'asking' until all the stocks' faith have been determined
    if holdings[smallestChain] >= 2 and biggestHotelStocks >= 1:
      #trades are 2 for 1
      #trade up by sending the order to buy largest

      if constants.LOGLEVEL>=1: print("we're going ahead and trading two %s stocks to buy one %s stocks!" % (smallestChain,biggestChain))
      rc, data = self.tb.tradeStocks(biggestChain, 1)
      if rc != 200: 
        print("ERROR - illegal move trying to liquidate (trade) stock\n%s" % data)
        print("ERROR - liquidateStocks (trade) system exit next")

    #we're down to one or none
    #sell in late game, retain in early game
    elif holdings[smallestChain] > 0 and len(self.gameinfo['game']['board']['occupied']) > (constants.MIDGAME):
      if constants.LOGLEVEL>=1: print("we're going to sell 1 %s stock" % smallestChain)
      rc, data = self.tb.sellStocks(smallestChain, 1)
      if rc != 200:
        print("ERROR - illegal move trying to liquidate (sell) stock\n%s" % data)
        print("ERROR - liquidateStocks(sell) system exit next")
      
    #if holdings remain after this, end turn (turn ends automagically otherwise)
    elif holdings[smallestChain] > 0:
      if constants.LOGLEVEL>=1: print("we're going to retain %s stocks from %s" % (holdings[smallestChain],smallestChain))
      rc, data = self.tb.endTurn()
      if rc != 200:
        print("ERROR - illegal move trying to liquidate (hold) stock\n%s" % data)
        print("ERROR - liquidateStocks (hold) system exit next")

  #calculate holdings?; if you're ahead, end, else keep on
  def considerEnding(self):
    ''' some logic to determine if we WANT to end the game
        returns True if we did ask to end the game '''
    ret=False
    if constants.LOGLEVEL>=1: print("!!!! endgame in sight")
    rc, data = self.tb.endGame()
    if rc != 200:
      print("ERROR - unable to end game\%s" % d)
      print("ERROR - considerEnding system exit next")
    else:
      if constants.LOGLEVEL>=1: print("endgame requested successfully")
      ret=True
    return ret
  
  def gameOver(self):
    if constants.LOGLEVEL>=1: print("endrequested state reached; tile coverage is %i/108" % len(self.gameinfo['game']['board']['occupied']))
     
    #declare winner
    if constants.LOGLEVEL>=1: print("------------ final scores -----------")
    if constants.LOGLEVEL>=1: print(self.gameinfo['game']['gamestate']['stateinfo']['finalscores'])
    #in previous version of the gamestate json, it was necessary to collapse the list of single-key dictionnaries into a flat dictionnary before sorting
    #scoreDict={key: value for scoreEntry in self.gameinfo['game']['gamestate']['stateinfo']['finalscores'] for key, value in scoreEntry.items()}
    #display the final results
    if constants.LOGLEVEL>=0: print("final results:\n%s" % sorted(self.gameinfo['game']['gamestate']['stateinfo']['finalscores'], key=lambda x: x['amount'], reverse=True)) #sort by value (decreasing)
    #self.socketio.disconnect() #this seems unnecessary and causes socket close errors
    if constants.LOGLEVEL>=2: print("gameOver exit next")
    #self.killAILoop() #nah, we'll stick around, maybe they'll reset the game?!

#converts the player name argument into a player id
#because working with names is more fun than working with ids :)
def resolvename(gameserver,gameid,playername):
  r = requests.get("{}/gamelobby/v1/games/{}".format(gameserver,gameid))
  playerdicts = json.loads(r.text)['game']['players']
  return next(item for item in playerdicts if item['name'] == playername).get('id')


#entry function parses command line argument and instantiates AI player
if __name__ == "__main__":

  if len(sys.argv) == 5:
    gameserver = sys.argv[4] 
    print("gameserver = %s" % gameserver)
  else:
    gameserver = "http://localhost:5000"
    
  if len(sys.argv) >= 4:
    style = sys.argv[3]
  else:
    style=None
  
  if len(sys.argv) >= 3:
    gameid = sys.argv[1]
    playername = sys.argv[2] #aiplayer will assume the identity of the first player with a matching name 
  else:
    print("incorrect number of arguments; invoke with:\n%s room playername [style] [http://gameserver:port]" % sys.argv[0])
    sys.exit()

  #convert name into a playerID
  playerid = resolvename(gameserver,gameid,playername)
  print("recovered player ID: %s" % playerid)
   
  #instantiates an AI player
  print("=================================================================") #line break in the log when spawning multiple games
  player=AggressiveTileBagAIPlayer(gameserver=gameserver, gameid=gameid, playerid=playerid)
   
  # Run the AI in it's own thread, mimicks what we do when launching from the server
  ailoop=player.runAILoop()

  # Since we're running as our own process already, just join that thread
  if ailoop:
    ailoop.join()
   
  # if we wanted to simulate how the server will call this, delete the join and do something like the following
  #do all sorts of other stuff, until we want to kill the AI
  #import time
  #time.sleep(10)
  #player.killAILoop()
  print("that thread must be dead!")
