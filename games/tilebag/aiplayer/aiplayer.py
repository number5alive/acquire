from games.tilebag.player import TileBagPlayer
import sys #handling command line parameters
import json #well, everything is json nowadays, isn't it?
import socketio #to be notified of game state changes
import requests #for GET/POST/PATCH http requests into the REST endpoints
import games.tilebag.aiplayer.constants as constants #for constants
from time import sleep #to optinonally simulate the human speed of play
import random #picking tiles at random for now
import threading #so we can still do other stuff while this player runs!

class TileBagAIPlayer(TileBagPlayer):
    #aiplayer constructor
    def __init__(self, id, name=None, money=6000, gameserver="http://localhost:5000", gameid="test", style="aggressive"):
        
        super().__init__(id, name=name)
        self._connected = False
        self.gameserver = gameserver
        self.gameid = gameid
        self.style = style
        self.RESTendpoints={"gamestate":"{}/tilebag/v1/{}".format(self.gameserver,self.gameid),
                "placetile":"{}/tilebag/v1/{}/board?playerid={}".format(self.gameserver,self.gameid,self.id),
                "buystocks":"{}/tilebag/v1/{}/stocks?playerid={}".format(self.gameserver,self.gameid,self.id),
                "endturn":"{}/tilebag/v1/{}/stocks?playerid={}".format(self.gameserver,self.gameid,self.id),
                "placehotel":"{}/tilebag/v1/{}/hotels?playerid={}".format(self.gameserver,self.gameid,self.id),
                "endgame":"{}/tilebag/v1/{}?playerid={}".format(self.gameserver,self.gameid,self.id)}
        if constants.LOGLEVEL>=1: print("%saiplayer constructed" % (style+" " if style else ""))

        #the ai player needs to receive websocket messages from the server to react to turn signals
        self.socketio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1, reconnection_delay_max=5, randomization_factor=0.5, logger=True, engineio_logger=True)

        #the websocket update messages happen very often and cause the turn handler routine to race with itself
        #we use the in_turn flag to "stop reacting" to update events while we're playing our moves
        self.in_turn = False
        self.lastPlayer = self.currentPlayer = None #only to reduce log verbosity
        #register socket event handlers, can't use decorator syntax within an class definition
        self.socketio.on('connect')(self._connect)
        self.socketio.on('update')(self._update)
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
        return ailoop
             
    def killAILoop(self):
      ''' called to stop the main ai loop (the socket wait), replaces the self.killAILoop calls '''
      print("Dropping connection to the websocket")
      self.socketio.disconnect() # this should abort the wait loop cleanly
      print("Connection Dropped")
      self._connected=False

    #this officially registers the player with the server and fetches the inital gamestate
    def join(self):
        #join message necessary to receive updates via websockets
        print("trying to join")
        self.socketio.emit('join', {'room':'{}'.format(self.gameid)})
        if constants.LOGLEVEL>=1: print("player joined %s" % self.gameserver) 
        self.fetchGameState()

    #this subroutine sends a request to the server's REST API to fetch the complete game state
    #(player's viewpoint) and parses the json to determine if it is the player's turn
    def fetchGameState(self):
        
        #print("fetching game state for user %s in room %s" % (self.id,self.gameid) )
        getparams = {"playerid": "{}".format(self.id)}
        r = requests.get(self.RESTendpoints.get("gamestate"),params=getparams)
        if r.status_code != 200:
            print("ERROR - error fetching game state\n%s" % r)
            print("ERROR - fetchGameState system exit next")
            self.killAILoop()

        #updating gamestate
        self.gamestate = json.loads(r.text)
        self.currentPlayer = self.gamestate['game']['gamestate']['currplayer']['id']
        if constants.LOGLEVEL>=2: print("...gamestate = %s (%s) ..." % (self.gamestate['game']['gamestate']['state'],self.gamestate['game']['gamestate']['currplayer']['name']))
        if constants.LOGLEVEL>=3: print("%s \n" % self.gamestate)
        
        if self.gamestate['game']['gamestate']['state'] == "EndGame":
            self.gameOver()

        if not self.in_turn and self.currentPlayer == self.id:
            self.turnHandler()
        elif self.currentPlayer != self.id and self.currentPlayer != self.lastPlayer:
        #a little less verbose in the console if we only show player turn once per turn
            if constants.LOGLEVEL>=1: print("oh look, it is %s's turn" % self.gamestate['game']['gamestate']['currplayer']['name'])
            self.lastPlayer = self.currentPlayer

    #this routine is invoked to handle the AI player's actions upon hits turn
    def turnHandler(self):
        sleep(constants.DELAYTIME)

        #insert logic to figure out what part of the turn
        self.in_turn = True
        if self.gamestate['game']['endrequested'] == True:
            self.endGame()
        elif self.gamestate['game']['endpossible'] == True:
            self.considerEnding()
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
        self.in_turn = False


    #this is where the AI will hopefully shine
    def placeTile(self):
        if constants.LOGLEVEL>=1: print("\nits our turn %s;\n my precious, we must play something, ..." % self.gamestate['game']['gamestate']['currplayer']['name'])
        #the server will reject illegal moves, so try at random until it works
        randomTileList = self.gamestate['game']['you']['playerdata']['tiles']
        random.shuffle(randomTileList)
        for tile in randomTileList:
            if constants.LOGLEVEL>=1: print("we think we'll play this tile %s" % tile)
            patchdata = {"action":"placetile","tile":"{}".format(tile)}
            if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("placetile")))
            r = requests.patch(self.RESTendpoints.get("placetile"),json=patchdata)
            if r.status_code == 200: 
                break
            else:
                print("ERROR - placing tile %s was rejected" % tile)
        if r.status_code != 200: 
            print("ERROR - we seem to have no valid tiles in our hand!!")
            print("ERROR - placeTile system exit next")
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
            self.killAILoop()

    #this is where the AI will also hopefully shine
    def buyStock(self):
        #let's buy the best stock we can afford (stock available and hotel on the board) if we have enough money
        money = self.gamestate['game']['you']['playerdata']['money']

        #print("buying stock action")
        #print("money {}".format(money))
        #print("style {}".format(self.style))
        #print("hotels {}".format(self.gamestate['game']['hotels']))
        #print("purchasable hotels {}".format([item for item in self.gamestate['game']['hotels'] if item['price'] is not None and item['stocks']>=2]))
        #print("purchasable hotels we can afford {}".format([item for item in self.gamestate['game']['hotels'] if item['price'] is not None and item['price']*2 < money and item['stocks']>=2]))
        if len([item for item in self.gamestate['game']['hotels'] if item['price'] is not None and item['price']*2 < money and item['stocks']>=2]) > 0:

            desiredStock=sorted(iter(item for item in self.gamestate['game']['hotels'] if item['price'] is not None and item['price']*2 < money and item['stocks']>=2), key = lambda i: i['price'],reverse=(True if self.style=="aggressive" else False))[0]
            if constants.LOGLEVEL>=1: print("desired stock: {}".format(desiredStock))
            
            if desiredStock is not None:
                if constants.LOGLEVEL>=1: print("we have $%s, and we think we'll buy two of the %s stock %s for $%s" % 
                        (money, "most expensive" if self.style=="aggressive" else "cheapest", desiredStock['name'],desiredStock['price']))
                patchdata = {"action":"buystocks","hotel":"{}".format(desiredStock['name']),"amount":2}
                if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("buystocks")))
                r = requests.patch(self.RESTendpoints.get("buystocks"),json=patchdata)
                if r.status_code != 200: print("illegal move trying to buy stock!\n%s" % r)
        else:
            if constants.LOGLEVEL>=1: print("we don't have a lot of money left (%i), or there are no stock we can buy currently" % money)

        if constants.LOGLEVEL>=1: print("we think we'll end our turn")
        patchdata = {"action":"buystocks","hotel":None,"amount":0}
        if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("endturn")))
        r = requests.patch(self.RESTendpoints.get("endturn"),json=patchdata)
        if r.status_code != 200: print("illegal move trying to end turn\n%s" % r) 

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
                    key= lambda i:i['majority'])[0]
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
            print("ERROR - selectMergeLoser system exit next")
            self.killAILoop()
        
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
            print("ERROR - selectMergeWinner system exit next")
            self.killAILoop()


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
                self.killAILoop()

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
                self.killAILoop()
            
        #if holdings remain after this, end turn (turn ends automagically otherwise)
        elif holdings[smallestChain] > 0:
            if constants.LOGLEVEL>=1: print("we're going to retain %s stocks from %s" % (holdings[smallestChain],smallestChain))
            patchdata = {"action":"buystocks","hotel":"Passing","amount":0}
            if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("endturn")))
            r = requests.patch(self.RESTendpoints.get("endturn"),json=patchdata)
            if r.status_code != 200:
                print("ERROR - illegal move trying to liquidate (hold) stock\n%s" % r)
                print("ERROR - liquidateStocks (hold) system exit next")
                self.killAILoop()


    #calculate holdings?; if you're ahead, end, else keep on
    def considerEnding(self):
        if constants.LOGLEVEL>=1: print("!!!! endgame in sight")
        patchdata = {"endgame":"yeahletsdoit"}
        if constants.LOGLEVEL>=3: print("patch data: %s\nendpoint: %s" % (patchdata,self.RESTendpoints.get("endgame")))
        r = requests.patch(self.RESTendpoints.get("endgame"),json=patchdata)
        if r.status_code != 200:
            print("ERROR - unable to end game\%s" % r)
            print("ERROR - considerEnding system exit next")
            self.killAILoop()
        else:
            if constants.LOGLEVEL>=1: print("endgame requested")
    
    def endGame(self):
        if constants.LOGLEVEL>=1: print("tile coverage is %i/108" % len(self.gamestate['game']['board']['occupied']))
        self.buyStock() #you're allowed to finish your turn

    def gameOver(self):
        #declare winner
        if constants.LOGLEVEL>=1: print("------------final scores -----------")
        if constants.LOGLEVEL>=1: print(self.gamestate['game']['gamestate']['stateinfo']['finalscores'])
        #in previous version of the gamestate json, it was necessary to collapse the list of single-key dictionnaries into a flat dictionnary before sorting
        #scoreDict={key: value for scoreEntry in self.gamestate['game']['gamestate']['stateinfo']['finalscores'] for key, value in scoreEntry.items()}
        #display the final results
        if constants.LOGLEVEL>=0: print("final results:\n%s" % sorted(self.gamestate['game']['gamestate']['stateinfo']['finalscores'], key=lambda x: x['amount'], reverse=True)) #sort by value (decreasing)
        self.socketio.disconnect()
        if constants.LOGLEVEL>=1: print("gameOver exit next")
        self.killAILoop()

    #event handler for socketio
    def _connect(self):
        if constants.LOGLEVEL>=1: print("connection established")
        self.join()


    #event handler for socketio
    def _update(self,data):
        #for now, all the WS messages suggest to fetch a new game state, so we shall oblige
        if constants.LOGLEVEL>=2: print("....websocket message received to update gamestate.... in_turn="+str(self.in_turn))
        if constants.LOGLEVEL>=3: print(data)
        self.fetchGameState()
        

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
    print("recoverd player ID: %s" % playerid)
    #instantiates an AI player
    print("=================================================================") #line break in the log when spawning multiple games
    player=TileBagAIPlayer(playerid, (playername + "+AI"), money=6000,gameserver=gameserver, gameid=gameid, style=style)
     
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


