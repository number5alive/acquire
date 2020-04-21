from flask import Flask
from flask import jsonify
from flask import request, abort
import base
import userif as UserIf
import dataif as DataIf
from games.tilebag.tilebag import TileBagGame, TileBagPlayer
 
TILEBAGREST_URL=TileBagGame.starturl()

# Expose these routes to the main server application 
from flask import Blueprint
tilebagrest_blueprint = Blueprint('tilebagrest_blueprint', __name__)
 
# Helper function - for now pull from request.arg, later from the auth token
def getCallingPlayerInfo(req_game):
  pinfo=None
   
  caller=UserIf.getCallingPlayerId()
  if caller:
    pinfo=req_game.getPlayerInfo(int(caller))
  return pinfo
 
# GET / Confirm Server is running
# TODO: return tilebag REST endpoints
@tilebagrest_blueprint.route('/', methods=['GET'])
def rest_tilebag_hello():
    return jsonify({'message' : 'Hello, World!'})
     
# GET /games/id Get details about a specific game
@tilebagrest_blueprint.route('/<int:gameid>', methods=['GET'])
def rest_tilebag_get_game_info(gameid):
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    ret={'game' : req_game.getPublicInformation()}
     
    # add private player info for the one that called in (if any)
    pinfo=getCallingPlayerInfo(req_game)
    if pinfo:
      ret['game']['you'] = pinfo
       
    return jsonify(ret)
  else:
    abort(404) #no such game

# PATCH /games/id used to take an action in the game
@tilebagrest_blueprint.route('/<int:gameid>', methods=['PATCH'])
def rest_tilebag_take_game_action(gameid):
  actions=['placetile', 'buystock']
   
  # make sure they've specified an action to take
  if not request.json or not 'action' in request.json or not request.json['action'] in actions:
    print("no json, no action, or invalid action")
    abort(400)
  req_action=request.json['action']

  # Find the game they want to run
  req_game=DataIf.getGameById(gameid)
  if req_game is None:
    print("some dummy just tried to twiddle with a non existent game")
    abort(400)

  # Make sure the callers is someone playing this game!
  pinfo=getCallingPlayerInfo(req_game)
  if pinfo is None:
    print("we're not going to let just anyone twiddle with the game!")
    abort(400)
    
  if req_action == 'placetile':
    req_tile=request.json['tile']
    if req_tile is None:
      print("No tile specified")
      abort(400)

    if req_game.playTile(pinfo['id'], alpha=req_tile):
      return jsonify({'success':True})
  abort(400)
