from flask import render_template
from flask import jsonify
from games.tiles import TileBag, Tile
import userif as UserIf
 
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

from lobby.lobbyrest import BASEURI as RESTURI
@tilebag_blueprint.route('/<int:gameid>', methods=['GET'])
def get_tilebag_clientif(gameid):
  userid=UserIf.getCallingPlayerId()
  return render_template('tilebag.html', gameid=gameid, userid=userid, baseuri=RESTURI)
   
