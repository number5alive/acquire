from flask import jsonify
from flask import request
#from games.tilebag.aiplayer.aiplayer import TileBagAIPlayer
from ai.tilebag.aiplayer import TileBagAIPlayer
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

# We'll store robots as [gameid][playerid]
_AITHREADS={}
 
def _makeAIThreadName(gameid, playerid): 
  return "T{}.{}.AI".format(gameid[-4:],playerid)
   
@tilebagairest_blueprint.route('/<string:gameid>', methods=['GET'])
def rest_tilebagai_games(gameid):
  ''' GET the number of AI players currently playing this game '''
  errno=200 #presume success
  robots={}
       
  if gameid in _AITHREADS:
    # quick check to see if old robots are still alive (they might have died since we last checked)
    deadbots=[]
    for playerid, robot in _AITHREADS[gameid].items():
      if not robot['thread'].is_alive():
        deadbots.append(playerid)  # two step since we'll be affecting the thing we're looping over

    #if any were dead, remove them from the list
    for p in deadbots:
      _AITHREADS[gameid].pop(p)

    # now we can confidently tell the caller how many robots are running
    robots=_AITHREADS[gameid]
       
  print("GETAI result for {}: {}".format(gameid, robots))
  # NOTE: the key in _AITHREADS is the playerid, which is what the caller will need anyway
  return jsonify({'robots': [k for k in robots.keys()]}), errno

@tilebagairest_blueprint.route('/<string:gameid>/<string:playerid>', methods=['POST'])
def rest_tilebagai_addai(gameid, playerid):
  ''' Make a player into a robot '''
  errno=200 #presume success
  errmsg="bot is running!"

  # Make sure the player isn't already a robot
  # TODO: the AI might be in this list but not actually running, check that
  if gameid not in _AITHREADS or playerid not in _AITHREADS[gameid]:
    print("Creating the AI player")
    aiName=_makeAIThreadName(gameid, playerid)
   
    player=TileBagAIPlayer(playerid, gameserver=request.host_url, gameid=gameid, style="aggressive")
    # we do this in a thread so it can run indepenent from the server
    # the event is used so we know when we can check if we connected successfully
    connectEvent=AIThreadEvent()
    aithread=Thread(target=_doAIThread, name=aiName, args=(connectEvent, player))
   # aithread=socketio.start_background_task(target=_doAIThread, args=(connectEvent, gameid, playerid))
    aithread.start()
    connectEvent.wait() # signals when we know the connection state
     
    # if we connect, this thread will live on, so keep track of it!
    if connectEvent.connected:
      robotinfo={'thread':aithread, 'player':player} # this really could be simpler eh? carry-over!
      if gameid not in _AITHREADS:
        _AITHREADS[gameid]={}
      _AITHREADS[gameid][playerid]=robotinfo
    else:
      errmsg="couldn't start the AI, likely a connection error"
      errno=500
  else:
    errno=409
    errmsg="There's already a bot for that!"

  print("ADDAI result {}: {}".format(errno, errmsg))
  return jsonify({'message': errmsg}), errno

@tilebagairest_blueprint.route('/<string:gameid>/<string:playerid>', methods=['DELETE'])
def rest_tilebagai_removeai(gameid, playerid):
  ''' Stop the AI from running for the specified player '''
  errno=501 #not implemented
  errmsg="Sorry, haven't implemented this yet"
  aiName=_makeAIThreadName(gameid, playerid)
       
  if gameid in _AITHREADS and playerid in _AITHREADS[gameid]:
    # if the thread is running, killing the TileBagAIPlayer will kill the thread
    if _AITHREADS[gameid][playerid]['thread'].is_alive():
      _AITHREADS[gameid][playerid]['player'].killAILoop()
    _AITHREADS[gameid].pop(playerid)
    errno=200
    errmsg="She's done!"
  else:
    errno=404
    errmsg="No AI running by that name!"
   
  return jsonify({'message': errmsg}), errno
