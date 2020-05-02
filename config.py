from games.tilebag.tilebag import TileBagGame
from flask import Flask
from flask_socketio import SocketIO
 
# Moving server config info here so we can get it from elsewhere too!
app = Flask(__name__,static_folder='clientweb/static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
 
# TODO: query for game subclasses and presume they can be loaded
# dictionary should be key=Class value=module
serverconfig={ 
  "version": 1,
  "games": [
    TileBagGame.config(),
  ]
}

def getGameInfo(gamename):
  for game in serverconfig["games"]:
    if game['name'] == gamename:
      return game
  return None

if __name__ == "__main__":
  print(serverconfig)
