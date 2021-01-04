from flask import jsonify
from flask import request
from games.tilebag.aiplayer.aiplayer import TileBagAIPlayer
from threading import Thread, Event

#
# The AI REST API is effectively "stand-alone" from the game
# I.e. The game itself knows NOTHING about the fact that AIs could exist
# This is somewhat by design - it would've been quicker perhaps to code the two together, but we
# didn't. This means that we need to track (and destroy) all the AI threads we create on the server
# or risk filling up the server with them
#

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

def _doAIThread(connectEvent, player):
  ''' A thread that boots up an AI player '''
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

_AITHREADS={}
 
def _makeAIName(gameid, playerid): 
  return "T{}.{}.AI".format(gameid[-4:],playerid)
   
@tilebagairest_blueprint.route('/<string:gameid>/<string:playerid>', methods=['POST'])
def rest_tilebagai_addai(gameid, playerid):
  ''' Make a player into a robot '''
  errno=200 #presume success
  errmsg="bot is running!"
  aiName=_makeAIName(gameid, playerid)

  # Make sure the player isn't already a robot
  if aiName not in _AITHREADS:
    print("Creating the AI player")
    print(_AITHREADS)
    player=TileBagAIPlayer(playerid, aiName, gameserver=request.host_url, gameid=gameid, style="aggressive")
    # we do this in a thread so it can run indepenent from the server
    # the event is used so we know when we can check if we connected successfully
    connectEvent=AIThreadEvent()
    aithread=Thread(target=_doAIThread, name=aiName, args=(connectEvent, player))
   # aithread=socketio.start_background_task(target=_doAIThread, args=(connectEvent, gameid, playerid))
    aithread.start()
    connectEvent.wait() # signals when we know the connection state
     
    # if we connect, this thread will live on, so keep track of it!
    if connectEvent.connected:
      _AITHREADS[aiName]={'thread':aithread, 'player':player}
    else:
      errmsg="couldn't start the AI, likely a connection error"
      errno=500
  else:
    errno=409
    errmsg="There's already a bot for that!"

  print("ADDAI result {}: {}".format(errno, errmsg))
  return jsonify({'message': errmsg}), errno

# TODO: API to make a player _stop_ being a robot
@tilebagairest_blueprint.route('/<string:gameid>/<string:playerid>', methods=['DELETE'])
def rest_tilebagai_removeai(gameid, playerid):
  ''' Stop the AI from running for the specified player '''
  errno=501 #not implemented
  errmsg="Sorry, haven't implemented this yet"
  aiName=_makeAIName(gameid, playerid)
       
  if aiName in _AITHREADS:
    # if the thread is running, get the player to kill the thread
    if _AITHREADS[aiName]['thread'].is_alive():
      _AITHREADS[aiName]['player'].killAILoop()
    _AITHREADS.pop(aiName)
    errno=200
    errmsg="She's done!"
  else:
    errno=404
    errmsg="No AI running by that name!"
   
  return jsonify({'message': errmsg}), errno
