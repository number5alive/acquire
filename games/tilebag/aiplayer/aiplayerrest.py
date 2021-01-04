from flask import jsonify
from flask import request
from games.tilebag.aiplayer.aiplayer import TileBagAIPlayer
from threading import Thread, Event


TILEBAGAIREST_URL='/ai'
 
# Expose these routes to the main server application 
from flask import Blueprint
tilebagairest_blueprint = Blueprint('tilebagiarest_blueprint', __name__)

@tilebagairest_blueprint.route('/', methods=['GET'])
def rest_tilebagai_hello():
  ''' GET the number of AI players currently playing games '''
  return jsonify({'message' : 'Hello, AI World!'})

class AIThreadEvent(Event):
  ''' Helper class so I can tell the calling engine that we connected okay '''
  def __init__(self):
    super().__init__()
    self.connected=False


def _doAIThread(connectEvent, gameid, playerid):
  ''' A thread that boots up an AI player '''
  gameserver = "http://localhost:5000"
  
  print("Creating the AI player")
  player=TileBagAIPlayer(playerid, "{}AI".format(playerid), money=6000,gameserver=gameserver, gameid=gameid, style="aggressive")

  # Run the AI loop - it'll let us know if the connection succeeds
  print("Starting the AI player")
  ailoop=player.runAILoop() # returns when connected OR when if that fails
   
  # now we know if the connection was established, signal that to the caller
  if ailoop:
    connectEvent.connected=True
  connectEvent.set()

  # if ailoop is set, then we're waiting on the socket, so life is groovy, join the two threads
  # this thread will just run more or less forever now
  if ailoop:
    ailoop.join()
   
@tilebagairest_blueprint.route('/<string:gameid>/<string:playerid>', methods=['POST'])
def rest_tilebagai_addai(gameid, playerid):
  ''' Make a player into a robot '''
       
  # we do this in a thread so it can run indepenent from the server
  # the event is used so we know when we can check if we connected successfully
  connectEvent=AIThreadEvent()
  aithread=Thread(target=_doAIThread, args=(connectEvent, gameid, playerid))
 # aithread=socketio.start_background_task(target=_doAIThread, args=(connectEvent, gameid, playerid))
  aithread.start()
  connectEvent.wait() # signals when we know the connection state
   
  errmsg="couldn't start the AI, likely a connection error"
  errno=500
   
  if connectEvent.connected:
    errmsg="bot is running!"
    errno=200
  return jsonify({'message': errmsg}), errno

