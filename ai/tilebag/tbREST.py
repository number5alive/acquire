import requests #for GET/POST/PATCH http requests into the REST endpoints
import json
from games.tilebag.tilebagrest import TILEBAGREST_URL

class TileBagREST:
  """ Helper class for issuing TileBag REST API calls from Python code

    If you're writing some python code to interact with TileBag via its REST interface, then this
    class is exactly what you need. This helper class knows NOTHING about the current state of a game.
    It merely wraps calls to the REST interface for you, and gives you the data back in a format that is
    most easily consumable.

    Functions return:
      response_code, json_data

    USAGE examples
     
    # create the helper
    tb=TileBagREST("http://localhost:5000", gameid="test", playerid="513")
    # get the game state
    rc, data = tb.getPublicInfo()
    response, data = tb.getPrivateInfo()
    # take game actions
    rc, data = ttb.placeTile("5A")
    rc, data = ttb.buyStocks("Worldwide", 2)
    rc, data = ttb.sellStocks("Worldwide", 3)
    rc, data = ttb.tradeStocks("Tower", 2) # this would ask to receive 2 Tower in exchange 
                                             for 4 of whatever the other hotel was
    rc, data = ttb.endGame() # triggers the end of the game if allowed
    rc, data = ttb.endTurn() # end your turn
    
  """
  def __init__(self, gameserver="http://localhost:5000", gameid="test", playerid="513"):
    """ Initialize the Helper - keep track of which game and player id we are interacting with by default """
    self.gameserver=gameserver
    self.resturl="{}{}".format(gameserver, TILEBAGREST_URL)
    self.gameid=gameid
    self.playerid=playerid

  def getPublicInfo(self, gameid=None):
    """ ask for the public game state """
    # unless the caller overrides it, presume we're doing this for the current game
    if gameid is None: gameid=self.gameid

    # GET url/<string:gameid>
    targeturl="{}/{}".format(self.resturl, gameid)
    #print(targeturl)
    r=requests.get(targeturl)
   
    return r.status_code, json.loads(r.text) if r.text else None

  def getPrivateInfo(self, gameid=None, playerid=None):
    """ ask for the game state, with the players private information too
        NOTE: The game will respond 200 so long as the gameid is right - if the playerid is wonky
              you'll still get the public game info. This might surprise you (it did for me). """
    # unless the caller overrides them, presume we're doing this for the current game and player
    if gameid is None: gameid=self.gameid
    if playerid is None: playerid=self.playerid

    # GET url/<string:gameid>?<string:playerid>
    targeturl="{}/{}".format(self.resturl, gameid)
    getparams = {"playerid": playerid}
    r=requests.get(targeturl, params=getparams)
     
    return r.status_code, json.loads(r.text) if r.status_code==200 else r.text

  def placeTile(self, tile, playerid=None, gameid=None):
    """ place a tile onto the board """
    # unless the caller overrides them, presume we're doing this for the current game and player
    if playerid is None: playerid=self.playerid
    if gameid is None: gameid=self.gameid

    targeturl="{}/{}/board".format(self.resturl, gameid)
    reqparams = {"playerid": playerid}
    patchdata = {"action":"placetile","tile":tile}
    
    r = requests.patch(targeturl, params=reqparams, json=patchdata)
    return r.status_code, json.loads(r.text) if r.status_code==200 else r.text

  def buyStocks(self, hotel, amount, playerid=None, gameid=None):
    """ purchase stocks of a given hotel """
    # unless the caller overrides them, presume we're doing this for the current game and player
    if playerid is None: playerid=self.playerid
    if gameid is None: gameid=self.gameid

    targeturl="{}/{}/stocks".format(self.resturl, gameid)
    reqparams = {"playerid": playerid}
    patchdata = {"action":"buystocks","hotel":hotel,"amount":amount}
    
    #print(patchdata)
    r = requests.patch(targeturl, params=reqparams, json=patchdata)
    return r.status_code, json.loads(r.text) if r.status_code==200 else r.text

  def sellStocks(self, hotel, amount, playerid=None, gameid=None):
    """ sell stocks in a given hotel
        NOTE: amount should be a positive integer (how many to sell) """
    return self.buyStocks(hotel, -amount, playerid, gameid) 

  def endTurn(self, playerid=None, gameid=None):
    """ end a player's turn """
    return self.buyStocks("NOOP", 0, playerid, gameid)

  def tradeStocks(self, hotel, amount, playerid=None, gameid=None):
    """ trade stocks 2-for-1
        NOTE: The game expects a "buy" action for the bigger of the two properties to indicate a trade
              So, if the game is in the RESOLVE MERGER state, we can issue a "Buy X of larger" action via
              this call. Behind the scenes the engine will debit you 2x the shares in the smaller of the
              hotels """
    return self.buyStocks(hotel, amount, playerid, gameid) 
     
  def placeHotel(self, hotel, location="lastplayed", playerid=None, gameid=None):
    """ Place a hotel onto the board """
    # unless the caller overrides them, presume we're doing this for the current game and player
    if playerid is None: playerid=self.playerid
    if gameid is None: gameid=self.gameid

    targeturl="{}/{}/hotels".format(self.resturl, gameid)
    reqparams = {"playerid": playerid}
    patchdata = {"action":"placeHotel","hotel":hotel,"tile":location}
    
    #print(patchdata)
    r = requests.patch(targeturl, params=reqparams, json=patchdata)
    return r.status_code, json.loads(r.text) if r.status_code==200 else r.text

  def removeHotel(self, hotel):
    """ the remove hotel action - it's actually just a placeHotel action with an empty location """
    return self.placeHotel(hotel, location="")
     
  def endGame(self, playerid=None, gameid=None):
    """ End the game """
    # unless the caller overrides them, presume we're doing this for the current game and player
    if playerid is None: playerid=self.playerid
    if gameid is None: gameid=self.gameid

    targeturl="{}/{}".format(self.resturl, gameid)
    reqparams = {"playerid": playerid}
    patchdata = {"endgame":"yeahletsdoit"}
    
    r = requests.patch(targeturl, params=reqparams, json=patchdata)
    return r.status_code, json.loads(r.text) if r.status_code==200 else r.text
     
  def saveGame(self, playerid=None, gameid=None):
    """ Save all of the game info (in a way that can be reloaded 
        TODO: add an optional savefile argument and just save that data for the caller """
    # unless the caller overrides them, presume we're doing this for the current game and player
    if playerid is None: playerid=self.playerid
    if gameid is None: gameid=self.gameid

    targeturl="{}/save/{}".format(self.resturl, gameid)
    reqparams = {"playerid": playerid}
    
    r = requests.get(targeturl, params=reqparams)
    return r.status_code, json.loads(r.text) if r.status_code==200 else r.text

  def loadGame(self, jsonfile, gameid=None):
    """ when/if implemented, it should cause the load of a game from a previously saved file 
        TODO: Implement this Yo! 
        NOTE: URL for loading is actually in the gamelobby
              POST gamelobby/v1/games """
    print("not implemented yet, but that'd be groovy eh?!")
    return 404, None

  def __str__(self):
    return "TileBag REST Helper - for {}, gameid={}, playerid={}".format(self.gameserver, self.gameid, self.playerid)

  def __repr__(self):
    return "TileBagREST(gameserver='{}', gameid='{}', playerid='{}')".format(self.gameserver, self.gameid, self.playerid)
           
# for running tests
if __name__ == "__main__":
  # Test the constructor, done different ways
  tb1=TileBagREST()
  tb2=TileBagREST(gameid="test2", playerid="777")
   
  print(str(tb1))
  print(repr(tb1))
  print(str(tb2))
  print(repr(tb2))

  print("The following only really works if the server is running on localhost::5000")

  print("====== Testing getPublicInfo ======")
  r, data = tb1.getPublicInfo()
  print(r)
  print(data)

  print("====== Testing getPrivateInfo (bad) ======")
  r, data = tb1.getPrivateInfo(playerid="asdfasdfasfas")
  print(r)
  print(data,)

  print("====== Testing getPrivateInfo (good) ======")
  r, data = tb1.getPrivateInfo()
  print(r)
  print(data)
  
  print("====== Testing placeTile ======")
  r, data = tb1.placeTile("7G")
  print(r)
  print(data)
   
  print("====== Testing buyStocks ======")
  r, data = tb1.buyStocks("Worldwide", 2)
  print(r)
  print(data)
   
  print("====== Testing sellStocks ======")
  r, data = tb1.sellStocks("Worldwide", 2)
  print(r)
  print(data)
   
  print("====== Testing tradeStocks ======")
  r, data = tb1.tradeStocks("Worldwide", 2)
  print(r)
  print(data)
   
  print("====== Testing endTurn ======")
  r, data = tb1.endTurn()
  print(r)
  print(data)
   
  print("====== Testing endGame ======")
  r, data = tb1.endGame()
  print(r)
  print(data)
   
  print("====== Testing saveGame ======")
  r, data = tb1.saveGame()
  print(r)
  print(data)
