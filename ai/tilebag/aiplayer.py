import sys #handling command line parameters
import json #well, everything is json nowadays, isn't it?
import socketio #to be notified of game state changes
import requests #for GET/POST/PATCH http requests into the REST endpoints
import games.tilebag.aiplayer.constants as constants #for constants
from time import sleep #to optinonally simulate the human speed of play
import random #picking tiles at random for now
import threading #so we can still do other stuff while this player runs!

class TileBagAIPlayer():
  ''' An AI that can play TileBag - shamelessly stolen from Fred's code and adapted to the new
      websocket messages that are available: yourturn, privateinfo, publicinfo '''
       
  #aiplayer constructor
  def __init__(self, playerid, gameserver="http://localhost:5000", gameid="test", style="aggressive"):
    self.id = playerid
    self.gameserver = gameserver
    self.gameid = gameid
    self.style = style
    self.unplayableTiles=[] #list to store tiles in our hand we've tried to play previously, wihout success
    self.currentPlayerState="" #used to concatenate current player and game state, and detect changes, to reduce log verbosity    
    self.RESTendpoints={"gamestate":"{}/tilebag/v1/{}".format(self.gameserver,self.gameid),
        "placetile":"{}/tilebag/v1/{}/board?playerid={}".format(self.gameserver,self.gameid,self.id),
        "buystocks":"{}/tilebag/v1/{}/stocks?playerid={}".format(self.gameserver,self.gameid,self.id),
        "endturn":"{}/tilebag/v1/{}/stocks?playerid={}".format(self.gameserver,self.gameid,self.id),
        "placehotel":"{}/tilebag/v1/{}/hotels?playerid={}".format(self.gameserver,self.gameid,self.id),
        "endgame":"{}/tilebag/v1/{}?playerid={}".format(self.gameserver,self.gameid,self.id),
        "savegame":"{}/tilebag/v1/save/{}".format(self.gameserver,self.gameid)}
    if constants.LOGLEVEL>=1: print("%saiplayer constructed" % (style+" " if style else ""))

    #the ai player needs to receive websocket messages from the server to react to turn signals
    #self.socketio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1, reconnection_delay_max=5, randomization_factor=0.5, logger=True, engineio_logger=True)
    self.socketio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1, reconnection_delay_max=5, randomization_factor=0.5)

    # in this version, we're actually only looking for the yourturn call, then doing
    # a full GET of the game state and taking an action
    #register socket event handlers, can't use decorator syntax within an class definition
    self.socketio.on('connect')(self._connect)
    #self.socketio.on('publicinfo')(self._publicinfo)
    #self.socketio.on('privateinfo')(self._privateinfo)
    self.socketio.on('yourturn')(self._yourturn)
    self.socketio.on('disconnect')(self._disconnect)

  def isConnected(self):
    return self._connected

  def runAILoop(self):
    ''' connect to the game, and wait for updates to the gamestate - best done in a thread! '''
    ailoop=None
    try:
      self.socketio.connect(self.gameserver, namespaces=['/'])
    except socketio.exceptions.ConnectionError as err:
      print("Failed to connect to the websocket")
    else:
      print("Connected!")
      ailoop=threading.Thread(target=self.socketio.wait)
      ailoop.start() # causes the AI loop to run
      self._connected=True

      # tell anyone that's listening, that there's a new robot in town!
      self.socketio.emit('clientmessage', {'room': self.gameid, 'message':'robots', 'robotaction': 'new', 'playerid': self.id})
    return ailoop
       
  def killAILoop(self):
    ''' called to stop the main ai loop (the socket wait), replaces the self.killAILoop calls '''
         
    # Before we drop the connection (TODO: test that we still HAVE that connection)
    # tell anyone that's listening, that there's a new robot in town!
    self.socketio.emit('clientmessage', {'room': self.gameid, 'message':'robots', 'robotaction': 'done', 'playerid': self.id})
         
    print("Dropping connection to the websocket")
    self.socketio.disconnect() # this should abort the wait loop cleanly
    print("Connection Dropped")
    self._connected=False

  #this officially registers the player with the server and fetches the inital gamestate
  def join(self):
    #join message necessary to receive updates via websockets
    print("trying to join")
    self.socketio.emit('join', {'room':'{}'.format(self.gameid)}) # for public info
    self.socketio.emit('join', {'room':'{}.{}'.format(self.gameid,self.id)}) # for private info
    if constants.LOGLEVEL>=1: print("player joined %s" % self.gameserver) 
    self.fetchGameState() # first time in, gotta grab the state
    self.turnHandler()

  #this subroutine simply sends a request to the server's REST API to fetch the complete game state
  #(player's viewpoint) 
  #it is called by the socketio event handling code _update as well as some elements of the playLoop
  def fetchGameState(self):
    if constants.LOGLEVEL>=2: print("fetching a new game state") #no gamestate information at this stage, until code below runs at least once
    getparams = {"playerid": "{}".format(self.id)}
    r = requests.get(self.RESTendpoints.get("gamestate"),params=getparams)
    if r.status_code != 200:
      print("ERROR - error fetching game state\n%s" % r)
    else:
      #updating gamestate
      self.previousPlayerState = self.currentPlayerState #storing previous value to determine change
      #loading and activating the full game state (should trap for errors here)
      self.gamestate = json.loads(r.text)
      #setting some utility fields
      self.currentPlayer = self.gamestate['game']['gamestate']['currplayer']['id']
      #concatenated snapshot of player and game state, used to determine changes
      self.currentPlayerState = "Player: {};  State: {}".format(self.gamestate['game']['gamestate']['currplayer']['name'], self.gamestate['game']['gamestate']['state'])
      if constants.LOGLEVEL>=2: print("currentPlayerState's string=> {}".format(self.currentPlayerState))
       
      #comparing previous to current player & state string, in order to limit logging once per turn/playstate
      if self.currentPlayerState != self.previousPlayerState:
        #simple logging
        if self.currentPlayer == self.id: 
          print("it's our turn, my precious, we must play someting {}".format(self.gamestate['game']['gamestate']['state']))
        else:
          print("oh look, it's {}'s turn to play someting {}".format(self.gamestate['game']['gamestate']['currplayer']['name'],self.gamestate['game']['gamestate']['state']))
          self.unplayableTiles = [] #just making sure; it shouldn't need it here, but....
        if constants.LOGLEVEL>=3: print(json.dumps(self.gamestate))
        if constants.LOGLEVEL>=4: 
          #obtain the server's viewpoint of the game state
          serverstate_req = requests.get(self.RESTendpoints.get("savegame"))
          if serverstate_req.status_code != 200:
            print("ERROR - error fetching server state\n%s" % serverstate_req)
          else:
            print("server state =>\n{}".format(serverstate_req.text))

      #this needs to happen regardless of who's turn it is; so it is not in the play loop
      if self.gamestate['game']['gamestate']['state'] == "EndGame":
        self.gameOver()


  #this subrouting tackles game play in a while loop
  def playLoop(self):
    #the while loop with a fetch state in it is useful to try different tiles if some are unplayable
    #it also addresses concurrency issues in which the aiplayer happens to be in a different state
    #than the server, which causes all attempted moves to fail
    # if not connected, then we know he game bailed somewhere
    while self.currentPlayer == self.id and self._connected:
      self.turnHandler()
      sleep(constants.DELAYTIME)
      self.fetchGameState() 

  #this routine is invoked to handle the AI player's actions upon its turn
  def turnHandler(self):

    # we only take an action if it's our turn
    # ... we shouldn't really get here othewise, but worth it to check
    if self.gamestate['game']['gamestate']['currplayer']['id'] == self.id:
      if self.gamestate['game']['endpossible'] == True and not self.gamestate['game']['endrequested'] == True and self.considerEnding():
        print("used this action to trigger end game - we'll get called again!")
      elif self.gamestate['game']['gamestate']['state'] == "PlaceTile":
        self.placeTile()
      elif self.gamestate['game']['gamestate']['state'] == "PlaceHotel": 
        self.placeHotel() 
      elif self.gamestate['game']['gamestate']['state'] == "BuyStocks": 
        self.buyStock()
      elif self.gamestate['game']['gamestate']['state'] == "TradeStock": 
        self.tradeStock()
      elif self.gamestate['game']['gamestate']['state'] == "SelectMergeLoser":
        self.selectMergeLoser()
      elif self.gamestate['game']['gamestate']['state'] == "SelectMergeWinner":
        self.selectMergeWinner()
      elif self.gamestate['game']['gamestate']['state'] == "LiquidateStocks":
        self.liquidateStocks()
      elif self.gamestate['game']['gamestate']['state'] == "EndGame":
        self.gameOver()


  #this is where the AI will hopefully shine
  def placeTile(self):
    #the server will reject illegal moves, so try at random until it works
    if constants.LOGLEVEL>=3: print("tile hand: {}".format(self.gamestate['game']['you']['playerdata']['tiles']))
    randomTileList = [tile for tile in self.gamestate['game']['you']['playerdata']['tiles']]
     
    while True:
      random.shuffle(randomTileList)

      if len(randomTileList)>0:
        tile = randomTileList.pop()
        if constants.LOGLEVEL>=1: print("we think we'll play this tile %s" % tile)
        patchdata = {"action":"placetile","tile":"{}".format(tile)}
        if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("placetile")))
        r = requests.patch(self.RESTendpoints.get("placetile"),json=patchdata)
        if r.status_code != 200: 
          print("ERROR - placing tile %s was rejected" % tile)
        else:
          return
           
    print("?!?! there are no (playable?) tiles in our hand!?")
    self.killAILoop()

  #this is where we place the hotel for which we have remaining stock and/or the most expensive stock
  def placeHotel(self):
    #find the most expensive hotel left (we shouldn't reach this code if there are no hotels left to place)
    #the datastructure is already ordered from cheapest to most expensive, so popping the last hotel from the list without a price
    hotelchain=list(iter(item for item in self.gamestate['game']['hotels'] if item['price'] is None))[-1]
    
    if constants.LOGLEVEL>=1: print("we think we'll launch this %s chain; it's worth the most" % hotelchain.get("name"))
    patchdata = {"action":"placeHotel","hotel":"{}".format(hotelchain.get("name")),"tile":"lastplaced"}
    if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("placehotel")))
    r = requests.patch(self.RESTendpoints.get("placehotel"),json=patchdata)
    if r.status_code != 200: 
      print("ERROR - illegal move trying to place a hotel\n%s" % r)
      print("ERROR - placeHotel system exit next")
      #self.killAILoop()

  #this is where the AI will also hopefully shine
  def buyStock(self):
    #let's buy the best stock we can afford (stock available and hotel on the board) if we have enough money
    money = self.gamestate['game']['you']['playerdata']['money']
    canbuy = self.gamestate['game']['gamestate']['stateinfo']['canbuy']

    # (smartly) try to buy stocks until it succeeds
    # when we pick 0 randomly it'll be the "no stock" action, so this will succeed eventually
    while True:
      # randomly select hotel and stocks to buy
      numtobuy=random.randint(0,canbuy)
      htobuy=random.choice([item for item in self.gamestate['game']['hotels'] if item['price'] is not None])

      # this is the "smartly" part (unless buying zero, make sure we have the ca$h or pick again)
      if numtobuy is not 0 and (htobuy['price']*numtobuy > money or htobuy['stocks']<numtobuy):
        continue
      
      # make the request to the server
      patchdata = {"action":"buystocks","hotel":htobuy['name'],"amount":numtobuy}
      if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("buystocks")))
      r = requests.patch(self.RESTendpoints.get("buystocks"),json=patchdata)

      # if it succeeds we're in business, if not (somewhat expected), that's okay
      if r.status_code != 200:
        print("illegal move trying to buy stock!\n%s" % r)
      else:
        break # needed so we only do one BuyStocks action per turn (otherwise we'll get out of sync)
    return

  #simple logic here
  def selectMergeLoser(self):
    mergeOptionsList = self.gamestate['game']['gamestate']['stateinfo']['smalloption']
    if constants.LOGLEVEL>=1: print("we must consider which chain will survive between %s" % mergeOptionsList)
    holdings = self.gamestate['game']['you']['playerdata']['stocks']
    hotels = self.gamestate['game']['hotels']

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
      elif [hotel for hotel in myHotels if hotel['ownstocks']>(constants.NUMSTOCKS-hotel['stocks'])/len(self.gamestate['game']['players'])]:
        hotelName = sorted(iter(hotel for hotel in myHotels if hotel['ownstocks']>
          (constants.NUMSTOCKS-hotel['stocks'])/len(self.gamestate['game']['players'])),
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
    #remove
    patchdata = {"action":"placeHotel","hotel":"{}".format(hotelName),"tile":None}
    if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("placehotel")))
    r = requests.patch(self.RESTendpoints.get("placehotel"),json=patchdata)
    if r.status_code != 200:
      print("ERROR - illegal move trying to remove a hotel\n%s" % r)
    
  def selectMergeWinner(self):
    mergeOptionsList = self.gamestate['game']['gamestate']['stateinfo']['bigoption']
    if constants.LOGLEVEL>=1: print("we must consider which chain will survive between %s" % mergeOptionsList)
    holdings = self.gamestate['game']['you']['playerdata']['stocks']
    hotels = self.gamestate['game']['hotels']

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
    patchdata = {"action":"placeHotel","hotel":"{}".format(selectedHotel['name']),"tile":"lastplaced"}
    if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("placehotel")))
    r = requests.patch(self.RESTendpoints.get("placehotel"),json=patchdata)
    if r.status_code != 200: 
      print("ERROR - illegal move trying to place a hotel to merge\n%s" % r)


  #will use simple logic here
  def liquidateStocks(self):
    #we don't need to handle the case of multiple hotel chains collapsing
    #(game server will request player's action for each in separate round robin turns)
    
    smallestChain = self.gamestate['game']['gamestate']['stateinfo']['smallest']
    biggestChain = self.gamestate['game']['gamestate']['stateinfo']['biggest'] #for stocks purchase orders
    holdings = self.gamestate['game']['you']['playerdata']['stocks']
    if constants.LOGLEVEL>=2: print("we must trade, sell and/or hold stock from %s (%i units) into %s (%i units)" % (smallestChain, holdings[smallestChain], biggestChain, holdings[biggestChain] if biggestChain in holdings else 0))

    #are there stock left to buy?
    biggestHotelStocks=next(hotel for hotel in self.gamestate['game']['hotels'] if hotel['name']==biggestChain)['stocks']
    if constants.LOGLEVEL>=2: print("holdings: %s" % holdings)
    if constants.LOGLEVEL>=2: print("biggestHotelStocks left to buy: %s" % biggestHotelStocks)

    #no need to loop, the server will keep 'asking' until all the stocks' faith have been determined
    if holdings[smallestChain] >= 2 and biggestHotelStocks >= 1:
      #trades are 2 for 1
      #trade up by sending the order to buy largest

      if constants.LOGLEVEL>=1: print("we're going ahead and trading two %s stocks to buy one %s stocks!" % (smallestChain,biggestChain))
      patchdata = {"action":"buystocks","hotel":"{}".format(biggestChain),"amount":1}
      if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("buystocks")))
      r = requests.patch(self.RESTendpoints.get("buystocks"),json=patchdata)
      if r.status_code != 200: 
        print("ERROR - illegal move trying to liquidate (trade) stock\n%s" % r)
        print("ERROR - liquidateStocks (trade) system exit next")

    #we're down to one or none
    #sell in late game, retain in early game
    elif holdings[smallestChain] > 0 and len(self.gamestate['game']['board']['occupied']) > (constants.MIDGAME):
      if constants.LOGLEVEL>=1: print("we're going to sell 1 %s stock" % smallestChain)
      patchdata = {"action":"buystocks","hotel":"{}".format(smallestChain),"amount":-1}
      if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("buystocks")))
      r = requests.patch(self.RESTendpoints.get("buystocks"),json=patchdata)
      if r.status_code != 200:
        print("ERROR - illegal move trying to liquidate (sell) stock\n%s" % r)
        print("ERROR - liquidateStocks(sell) system exit next")
      
    #if holdings remain after this, end turn (turn ends automagically otherwise)
    elif holdings[smallestChain] > 0:
      if constants.LOGLEVEL>=1: print("we're going to retain %s stocks from %s" % (holdings[smallestChain],smallestChain))
      patchdata = {"action":"buystocks","hotel":"Passing","amount":0}
      if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("endturn")))
      r = requests.patch(self.RESTendpoints.get("endturn"),json=patchdata)
      if r.status_code != 200:
        print("ERROR - illegal move trying to liquidate (hold) stock\n%s" % r)
        print("ERROR - liquidateStocks (hold) system exit next")

  #calculate holdings?; if you're ahead, end, else keep on
  def considerEnding(self):
    ''' some logic to determine if we WANT to end the game
        returns True if we did ask to end the game '''
    ret=False
    if constants.LOGLEVEL>=1: print("!!!! endgame in sight")
    patchdata = {"endgame":"yeahletsdoit"}
    if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("endgame")))
    r = requests.patch(self.RESTendpoints.get("endgame"),json=patchdata)
    if r.status_code != 200:
      print("ERROR - unable to end game\%s" % r)
      print("ERROR - considerEnding system exit next")
    else:
      if constants.LOGLEVEL>=1: print("endgame requested successfully")
      ret=True
    return ret
  
  def gameOver(self):
    if constants.LOGLEVEL>=1: print("endrequested state reached; tile coverage is %i/108" % len(self.gamestate['game']['board']['occupied']))
     
    #declare winner
    if constants.LOGLEVEL>=1: print("------------ final scores -----------")
    if constants.LOGLEVEL>=1: print(self.gamestate['game']['gamestate']['stateinfo']['finalscores'])
    #in previous version of the gamestate json, it was necessary to collapse the list of single-key dictionnaries into a flat dictionnary before sorting
    #scoreDict={key: value for scoreEntry in self.gamestate['game']['gamestate']['stateinfo']['finalscores'] for key, value in scoreEntry.items()}
    #display the final results
    if constants.LOGLEVEL>=0: print("final results:\n%s" % sorted(self.gamestate['game']['gamestate']['stateinfo']['finalscores'], key=lambda x: x['amount'], reverse=True)) #sort by value (decreasing)
    #self.socketio.disconnect() #this seems unnecessary and causes socket close errors
    if constants.LOGLEVEL>=2: print("gameOver exit next")
    #self.killAILoop() #nah, we'll stick around, maybe they'll reset the game?!

  #event handler for socketio
  def _connect(self):
    if constants.LOGLEVEL>=1: print("connection established")
    self.join()

  def _publicinfo(self, data):
    print('got public info: {}'.format(data))

  def _yourturn(self, data):
    print("It's my turn!")
    print('yourturn data: {}'.format(data))
    #self.fetchGameState() # game's waiting on us, pull the state and make a move
    self.gamestate = data
    self.turnHandler()

  def _privateinfo(self, data):
    print('got private info: {}'.format(data))

  #event handler for socketio
  def _disconnect(self):
    print("ERROR - we have been disconnected by a socket; let's abort cleanly")
    print("ERROR - socketio handler exit next")
    self.killAILoop()

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
  player=TileBagAIPlayer(playerid, gameserver=gameserver, gameid=gameid, style=style)
   
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
