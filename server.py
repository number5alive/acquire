from flask import Flask
from flask import url_for, send_from_directory, render_template
from flask import request
import os
from lobby.lobbyrest import lobbyrest_blueprint
from games.tilebag.tilebagrest import tilebagrest_blueprint, TILEBAGREST_URL
from games.tilebag.aiplayer.aiplayerrest import tilebagairest_blueprint, TILEBAGAIREST_URL
from clientweb.test import testview_blueprint
from clientweb.lobby import lobby_blueprint
from clientweb.tilebag import tilebag_blueprint, TILEBAG_URL
import dataif
from flask_socketio import SocketIO, join_room, rooms, emit

from config import app, socketio
 
# all the backend stuff that actually does stuff   
app.register_blueprint(lobbyrest_blueprint)
app.register_blueprint(tilebagrest_blueprint, url_prefix=TILEBAGREST_URL)
app.register_blueprint(tilebagairest_blueprint, url_prefix=TILEBAGAIREST_URL)

# Client-side view of things
app.register_blueprint(lobby_blueprint, url_prefix='/') # the lobby
app.register_blueprint(testview_blueprint, url_prefix='/test') # for testing
app.register_blueprint(tilebag_blueprint, url_prefix=TILEBAG_URL)

@app.route('/favicon.ico')
def favicon():
  ficodir=os.path.join(app.root_path, 'clientweb/static')
  print(ficodir)
  return send_from_directory(ficodir, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
 
@app.route('/', methods=['GET'])
def show_landing():
  """ Landing Page """
  return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print("websocket connection")

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print("user {} is now in rooms: {}".format(request.sid, rooms(request.sid)))

@socketio.on('clientmessage')
def on_clientmessage(data):
    """ websocket: relay node for clients to send notifications to others """
    room = data['room']
    message = data['message']

    # Just forward all the received message to the specified room
    socketio.emit(message, data, room=room)

# This is just a test endpoint for sending messages via the websocket
from flask import jsonify
@app.route('/message/<string:room>/<string:message>')
def ahhh(room, message):
    socketio.emit('update', {'message': message}, room=room)
    return jsonify({'message' : message})

    
# Required since running Flask in debug modes kicks it off twice
# this code will be run any time we have the first caller to our webserver
@app.before_first_request
def before_first_request():
  dataif.readGameStates()

if __name__ == "__main__":
  app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # stops the browser from caching

  socketio.run(app, host='0.0.0.0', port='5000', debug=True)
  #app.run(debug=True)
  print("server stopping")


