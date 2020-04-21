from flask import render_template
from flask import jsonify
from games.tiles import TileBag, Tile
 
"""
This file contains the "client" portion of the tilebag game
I.e. what the user will directly interact with, it leverages calls to the
     tilebagrest interface
"""
 
# Expose these routes to the main server application 
from flask import Blueprint
tilebag_blueprint = Blueprint('tilebag_blueprint', __name__,
                  template_folder='templates', static_folder='static')

@tilebag_blueprint.route('/', methods=['GET'])
def get_tilebag_api():
  return jsonify({'success' : 'true'})

