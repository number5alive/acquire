from flask import render_template
from flask import jsonify
from lobby.lobbyrest import BASEURI as RESTURI
from games.tiles import TileBag, Tile
import json
 
# Expose these routes to the main server application 
from flask import Blueprint
testview_blueprint = Blueprint('testview_blueprint', __name__,
                  template_folder='templates', static_folder='static')

""" Test endpoint for rendering tiles """
@testview_blueprint.route('/tiles', methods=['GET'])
def get_tiles():
  bag = TileBag(9,12)
  tiles=[str(bag.takeTile()) for i in range(0,7)]
  return jsonify({'tiles' : tiles})
   
""" A pretty little javascript viewer for the tiles """
@testview_blueprint.route('/tile', methods=['GET'])
def get_tiletest():
  return render_template('showtiles.html', baseuri=RESTURI, gameid=8, playerid=9, debug=json.dumps(True))
 
""" Test endpoint for rendering an acquire board """
@testview_blueprint.route('/board', methods=['GET'])
def get_boardtest():
  return render_template('board.html', baseuri=RESTURI)
