from flask import Flask, render_template
from flask import jsonify
from flask import request, abort
from Game import Game
from Player import Player

app = Flask(__name__)
BASEURI="/acquire/v1"

games=[Game(id) for id in range(0,2)]
print(games)

"""
API
GET / Confirm Server is running
GET /games List of existing games on the server
GET /games?id= Get details about a specific game
POST /games {'id'} Start a game
"""
 
@app.route(BASEURI + '/', methods=['GET'])
def hello_world():
    return jsonify({'message' : 'Hello, World!'})
     
def getGameById(id):
  for i,q in enumerate(games):
    currId=q.getId()
    if currId == id:
      return games[i]
  return None

def getGameByReq():
  req_id=request.values.get('gameid')
  req_game=None
  if req_id is not None and req_id.isdigit():
    req_id=int(req_id) # we read it from the request as a string
    req_game=getGameById(req_id)
  return req_id, req_game
 
@app.route(BASEURI + '/games', methods=['GET'])
def get_games():
  req_id, req_game = getGameByReq()
  if req_id is not None:
    print("get one game: " + str(req_id))
    if req_game is not None:
      return jsonify({'game' : req_game.serialize()})
    else:
      abort(404) #no such game
  else:
    return jsonify({'games' : [game.getId() for game in games]})

@app.route(BASEURI + '/players', methods=['GET'])
def get_players():
  req_gameid, req_game = getGameByReq()
  if req_game is not None:
    num_players, players=req_game.getPlayers()
    return jsonify({'players' : [player.getName() for player in players]})
  abort(404)
     
@app.route(BASEURI + '/players', methods=['POST'])
def add_player():
  print(request.json)
  if not request.json or not 'gameid' in request.json or not 'name' in request.json:
    print("something wrong with the json")
    abort(400)

  print("hey, we know what we need to know!")
  game = getGameById(request.json['gameid'])
  if game is None:
    abort(404)

  print("cool cool, add this player to the game!")
  game.addPlayer(Player(100,name=request.json['name']))
   
  abort(404)
     
""" Test endpoint for rendering tiles """
from Tiles import TileBag, Tile
@app.route(BASEURI + '/tiles', methods=['GET'])
def get_tiles():
  bag = TileBag(9,12)
  tiles=[str(bag.takeTile()) for i in range(0,7)]
  return jsonify({'tiles' : tiles})
   
@app.route(BASEURI + '/tiletest', methods=['GET'])
def get_tiletest():
  return render_template('showtiles.html')
 
"""
@app.route(BASEURI + '/games', methods=['POST'])
def startGame():
  req_id, req_game = getGameByReq()
  print(req_id)
  print(req_game)
  if req_id and req_game:
    if req_game.isStarted():
      abort(500)
    else:
      req_game.start()
      return jsonify({'game' : req_game.serialize()})
  abort(404)
"""

if __name__ == "__main__":
  playerIdCount=0
  app.run(debug=True)
     

