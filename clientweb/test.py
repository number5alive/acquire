from flask import render_template
from flask import jsonify
from restengine.lobbyrest import BASEURI as RESTURI
from games.tiles import TileBag, Tile
 
# Expose these routes to the main server application 
from flask import Blueprint
testview_blueprint = Blueprint('testview_blueprint', __name__,
                  template_folder='templates', static_folder='static')

BASEURI=''

""" Test endpoint for rendering tiles """
@testview_blueprint.route(BASEURI + '/tiles', methods=['GET'])
def get_tiles():
  bag = TileBag(9,12)
  tiles=[str(bag.takeTile()) for i in range(0,7)]
  return jsonify({'tiles' : tiles})
   
""" A pretty little javascript viewer for the tiles """
@testview_blueprint.route(BASEURI + '/tile', methods=['GET'])
def get_tiletest():
  return render_template('showtiles.html', baseuri=BASEURI)
 
""" Test endpoint for rendering an acquire board """
@testview_blueprint.route(BASEURI + '/board', methods=['GET'])
def get_boardtest():
  return render_template('board.html', baseuri=RESTURI)
