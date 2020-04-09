from flask import Flask
from restengine.lobbyrest import lobbyrest_blueprint
from clientweb.tilesview import tilesview_blueprint
from clientweb.lobby import lobby_blueprint

app = Flask(__name__)
app.register_blueprint(lobbyrest_blueprint)
app.register_blueprint(tilesview_blueprint)
app.register_blueprint(lobby_blueprint)
   
if __name__ == "__main__":
  app.run(debug=True)
