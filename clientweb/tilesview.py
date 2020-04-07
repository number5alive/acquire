from flask import render_template
from flask import jsonify
from restengine.lobbyrest import BASEURI
from games.tiles import TileBag, Tile
 
# Expose these routes to the main server application 
from flask import Blueprint
tilesview_blueprint = Blueprint('tilesview_blueprint', __name__,
                  template_folder='templates')

#BASEURI="/acquire/v1" #for now, we'll move this later
 
""" Test endpoint for rendering tiles """
@tilesview_blueprint.route(BASEURI + '/tiles', methods=['GET'])
def get_tiles():
  bag = TileBag(9,12)
  tiles=[str(bag.takeTile()) for i in range(0,7)]
  return jsonify({'tiles' : tiles})
   
""" A pretty little javascript viewer for the tiles """
@tilesview_blueprint.route(BASEURI + '/tiletest', methods=['GET'])
def get_tiletest():
  return render_template('showtiles.html', baseuri=BASEURI)
 
