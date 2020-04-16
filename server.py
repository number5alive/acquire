from flask import Flask
from restengine.lobbyrest import lobbyrest_blueprint
from games.tilebag.tilebagrest import tilebagrest_blueprint, TILEBAGREST_URL
from clientweb.test import testview_blueprint
from clientweb.lobby import lobby_blueprint
from clientweb.tilebag import tilebag_blueprint

app = Flask(__name__)
# all the backend stuff that actually does stuff   
app.register_blueprint(lobbyrest_blueprint)
app.register_blueprint(tilebagrest_blueprint, url_prefix=TILEBAGREST_URL)

# Client-side view of things
app.register_blueprint(lobby_blueprint) # the lobby
app.register_blueprint(testview_blueprint, url_prefix='/test') # for testing
app.register_blueprint(tilebag_blueprint, url_prefix=TILEBAGREST_URL)
   
if __name__ == "__main__":
  app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # stops the browser from caching
  app.run(debug=True)

