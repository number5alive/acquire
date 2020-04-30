from flask import render_template
from flask import jsonify
from flask import current_app as app
from flask import redirect, url_for
from lobby.lobbyrest import BASEURI
import dataif as DataIf
 
# Expose these routes to the main server application 
from flask import Blueprint
lobby_blueprint = Blueprint('lobby_blueprint', __name__,
                  template_folder='templates', static_folder='static')

""" Test endpoint for rendering tiles """
@lobby_blueprint.route('/lobby', methods=['GET'])
def show_lobby():
  return render_template('lobby.html', lobbyrest=BASEURI)

# for deleting games at the click of a button
@lobby_blueprint.route('/admin', methods=['GET'])
def lobby_admin_panel():
  abort(404)
   
def getStaticMaxChangeTime():
  import os
  import time

  staticdir=os.path.join(app.root_path, 'clientweb/static')
  return (max(os.stat(root).st_mtime for root,_,_ in os.walk(staticdir)))
   
# for creating and starting new games at the poke of URL
@lobby_blueprint.route('/<string:gname>', methods=['GET'])
def lobby_new_game(gname):
  CACHEFIX="?{}".format(int(getStaticMaxChangeTime()))
   
  # see if the game exists, and if not, create it
  req_game=DataIf.getGameById(gname)
  if req_game is None:
    print("trying to start a new game?")
    # for now, we only have TileBag on the server, so default to that
    req_game=DataIf.createGame("TileBag", gname)
 
  # if the game hasn't started, show the page for adding players and starting
  if not req_game.started:
    return render_template('newgame.html', gname=gname, lobbyrest=BASEURI, cachefix=CACHEFIX)

  else:
    print("redirect to the actual, running game")
    return redirect(url_for('tilebag_blueprint.get_tilebag_clientif', gameid=gname))
    
   
