from flask import Flask
from flask import jsonify
from flask import request, abort
import base
import dataif as DataIf
from games.tilebag.tilebag import TileBagGame, TileBagPlayer
 
TILEBAGREST_URL=TileBagGame.starturl()

# Expose these routes to the main server application 
from flask import Blueprint
tilebagrest_blueprint = Blueprint('tilebagrest_blueprint', __name__)
 
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
    #TODO: check to see if a playerID token is embedded in this request (cookie)
    #      use that to provide all the private player details 
    ret={'game' : req_game.getPublicInformation()}
    caller=request.args.get('playerid')
    print("playerinfo={}".format(caller))
    if caller:
      pi=req_game.getPlayerInfo(int(caller))
      if pi:
        ret['playerid'] = pi
      else:
        abort(404) #invalid player id
    return jsonify(ret)
  else:
    abort(404) #no such game

