import socketio #to be notified of game state changes
import ai.tilebag.constants as constants #for constants
from time import sleep #to optinonally simulate the human speed of play
import threading #so we can still do other stuff while this player runs!
from ai.tilebag.tbREST import TileBagREST #to make the calls over to the REST Engine

class TileBagBASEAIPlayer():
  ''' The "glue" for any AI/Automata that can play TileBag - shamelessly stolen from Fred's code and adapted 
       - uses the new websocket messages that are available: yourturn
       - uses the new TileBagREST helper class to tidy things up a bit
       - abstracts out the connection to game logic from the "smarts"
      '''
       
  def __init__(self, gameserver="http://localhost:5000", gameid="test", playerid="513"):
    self.gameserver = gameserver
    self.playerid = playerid
    self.gameid = gameid
    self.tb = TileBagREST(gameserver, gameid=gameid, playerid=playerid)
   
    if constants.LOGLEVEL>=1: print("BASE aiplayer constructed")

    #the ai player needs to receive websocket messages from the server to react to turn signals
    #self.socketio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1, reconnection_delay_max=5, randomization_factor=0.5, logger=True, engineio_logger=True)
    self.socketio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1, reconnection_delay_max=5, randomization_factor=0.5)

    # in this version, we're actually only looking for the yourturn calls, which will have all the data
    #register socket event handlers, can't use decorator syntax within an class definition
    self.socketio.on('connect')(self._connect)
    self.socketio.on('yourturn')(self._yourturn)
    self.socketio.on('disconnect')(self._disconnect)

  def isConnected(self):
    ''' lets the caller know if we have a stable websocket connection or not '''
    return self._connected

  @property
  def done(self):
    return self.currstate == "EndGame"

  def runAILoop(self):
    ''' connect to the game, and wait for updates to the gamestate - best done in a thread! '''
    ailoop=None
    try:
      self.socketio.connect(self.gameserver, transports=['polling'], namespaces=['/'])
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
         
    # Before we drop the connection (TODO: test that we still HAVE that connection)
    # tell anyone that's listening, that there's a new robot in town!
    self.socketio.emit('clientmessage', {'room': self.gameid, 'message':'robots', 'robotaction': 'done', 'playerid': self.playerid})
         
    print("Dropping connection to the websocket")
    self.socketio.disconnect() # this should abort the wait loop cleanly
    print("Connection Dropped")
    self._connected=False

  #event handler for socketio
  def _connect(self):
    ''' called when we first connect via the websocket - we'll immediate try to join the right channel '''
    if constants.LOGLEVEL>=1: print("connection established")

    #the following officially registers the player with the server and fetches the inital gamestate
         
    print("trying to join") #join message necessary to receive updates via websockets
    self.socketio.emit('join', {'room':'{}'.format(self.gameid)}) # for public info
    self.socketio.emit('join', {'room':'{}.{}'.format(self.gameid,self.playerid)}) # for private info
    if constants.LOGLEVEL>=1: print("player joined %s" % self.gameserver) 
     
    # first time in, gotta grab the state
    rc, gameinfo = self.tb.getPrivateInfo()
    if rc == 200:
      # tell anyone that's listening, that there's a new robot in town!
      # done if we've connected and successfully pulled some data
      self.socketio.emit('clientmessage', {'room': self.gameid, 'message':'robots', 'robotaction': 'new', 'playerid': self.playerid})
       
      # make sure to parse the gameinfo into something that's easy for us to use, then handle it
      self.parseGameState(gameinfo)
      self.turnHandler()

  def _yourturn(self, data):
    ''' websocket message indicating that it's our turn to act '''
    print("It's my turn!")
    print('yourturn data: {}'.format(data))
    self.parseGameState(data)
    self.turnHandler()

  def _disconnect(self):
    ''' triggered when the websocket connection drops '''
    print("ERROR - we have been disconnected by a socket; let's abort cleanly")
    print("ERROR - socketio handler exit next")
    self.killAILoop()

  def parseGameState(self, data):
    ''' helper function that just pulls short-hands from the gamestate data for us '''
    self.gameinfo=data
    self.currplayer=self.gameinfo['game']['gamestate']['currplayer']['id']
    self.currstate=self.gameinfo['game']['gamestate']['state']
    self.myinfo=self.gameinfo['game']['you']['playerdata']

  # Subclasses: Overwrite this!
  def turnHandler(self):
    ''' The Inheriting class should implement this if they want to do ANYTHING '''
    print("Hanlding Turn Logic - hope the inheriting class overrides this function!")


#entry function parses command line argument and instantiates AI player
if __name__ == "__main__":
  # test connecting an AI player to the server
  print("===== Constructing the Base AI Player ======")
  ai=TileBagBASEAIPlayer()

  # tell it to start running
  print("===== Starting the Base AI Player (should connect to the game) ======")
  ai.runAILoop()

  # give it some time to taste the freedom of life!
  print("Sleeping for a bit just for drama")
  for i in range(5):
    print(".", end='')
    sleep(1)
  print("That was fun")

  # tell it to stop running
  print("===== Stopping the Base AI Player =====")
  ai.killAILoop()

