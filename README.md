Just some playing round with Python and Web Stuff, using "make a python version of the boardgame Acquire" as an excuse.

### File organization
server.js - the flask web server, loading all the blueprints (sub-pages)
lobby/lobbyrest - a REST interface for listing games and (eventually) asking to join them
games - the python code that encapsulates the games themselves
games/tilebag - what is becoming, mostly, an acquire implementation
clientweb - a client that visits the lobby and can play/render the game

### About coding choices
Mostly this project was to play around with some 'raw' technologies, so I don't use a lot of plugins and frameworks that likely would have made this trivial. It's ultimately just python, javascript, and css. I used flask for the webserver, and a last-minute addition of the flask-socketio plugin was to enable real-time-ish notification of other clients when someone makes a change to the game state - right now it just instructs the client to fetch the game state again via the REST interface

### Running / Testing the code
Create a virtual-env and install the dependencies
(virtual-env) $ pip3 install -r requirements.txt
NOTE: run these apps from the root folder via:
(virtual-env) $ python3 -m server
 - then launch a browser and point to: localhost:5000/test/tile

# to test the game classes (unit tests)
(virtual-env) $ python3 -m games.tilebag.player
(virtual-env) $ python3 -m games.tilebag.tiles
(virtual-env) $ python3 -m games.tilebag.board
(virtual-env) $ python3 -m games.tilebag.hotels
(virtual-env) $ python3 -m games.tilebag.tilebag

# to play the game
Run the server (see above). Then navigate to <localhost:5000/somestring>, it'll let you create and start a game.
 
# to load a save game (or a test one)
$ curl -i -H "Content-Type: application/json" -X POST -d @t3.json http://localhost:5000/gamelobby/v1/games

