from flask import render_template
from flask import current_app as app
from flask import jsonify
from flask import request
from games.tilebag.tiles import TileBag, Tile
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

def getStaticMaxChangeTime():
  import os
  import time

  staticdir=os.path.join(app.root_path, 'clientweb/static')
  return (max(os.stat(root).st_mtime for root,_,_ in os.walk(staticdir)))
   

@tilebag_blueprint.route('/<string:gameid>', methods=['GET'])
def get_tilebag_clientif(gameid):
  playerid=UserIf.getCallingPlayerId()
   
  # I was having difficulting with static files being cached between the
  # server and the caller, this makes sure if we change those files it'll
  # be okay
  CACHEFIX=int(getStaticMaxChangeTime())
  print("CACHEFIX={}".format(CACHEFIX))
     
  return render_template('tilebag.html', gameid=gameid, playerid=playerid, serverroot=request.host, debug=json.dumps(False), cachefix="?{}".format(CACHEFIX))
   
