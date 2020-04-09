from flask import render_template
from flask import jsonify
from restengine.lobbyrest import BASEURI
 
# Expose these routes to the main server application 
from flask import Blueprint
lobby_blueprint = Blueprint('lobby_blueprint', __name__,
                  template_folder='templates')

""" Test endpoint for rendering tiles """
@lobby_blueprint.route('/lobby.html', methods=['GET'])
def show_lobby():
  return render_template('lobby.html', lobbyrest=BASEURI)
   
