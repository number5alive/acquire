from flask import render_template
from flask import jsonify
from flask import request
from games.tiles import TileBag, Tile
import userif as UserIf
import json
 
"""
This file contains the "client" portion of the tilebag game
I.e. what the user will directly interact with, it leverages calls to the
     tilebagrest interface
"""

TILEBAG_URL="/games/tilebag"
 
# Expose these routes to the main server application 
from flask import Blueprint
tilebag_blueprint = Blueprint('tilebag_blueprint', __name__,
                  template_folder='templates', static_folder='static')

@tilebag_blueprint.route('/', methods=['GET'])
def get_tilebag_api():
  return jsonify({'success' : 'true'})

@tilebag_blueprint.route('/<int:gameid>', methods=['GET'])
def get_tilebag_clientif(gameid):
  playerid=UserIf.getCallingPlayerId()
  return render_template('showtiles.html', gameid=gameid, playerid=playerid, serverroot=request.url_root, debug=json.dumps(False))
   
