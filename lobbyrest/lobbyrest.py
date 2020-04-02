from flask import Flask, render_template
from flask import jsonify
from flask import request, abort
from acquire.game import Game
from acquire.player import Player

BASEURI="/acquire/v1"
 
# Expose these routes to the main server application 
from flask import Blueprint
lobbyrest_blueprint = Blueprint('lobbyrest_blueprint', __name__)

games=[Game(id) for id in range(0,2)]
print(games)

"""
API
POST /games/id Start a game
"""
 
# GET / Confirm Server is running
@lobbyrest_blueprint.route(BASEURI + '/', methods=['GET'])
def hello_world():
    return jsonify({'message' : 'Hello, World!'})
     
def getGameById(id):
  for i,q in enumerate(games):
    currId=q.getId()
    if currId == id:
      return games[i]
  return None
 
# GET /games List of existing games on the server
@lobbyrest_blueprint.route(BASEURI + '/games', methods=['GET'])
def get_all_games():
  return jsonify({'games' : [game.getId() for game in games]})
   
# GET /games/id Get details about a specific game
@lobbyrest_blueprint.route(BASEURI + '/games/<int:gameid>', methods=['GET'])
def get_gameinfo(gameid):
  req_game=getGameById(gameid)
  if req_game is not None:
    return jsonify({'game' : req_game.serialize()})
  else:
    abort(404) #no such game

@lobbyrest_blueprint.route(BASEURI + '/players', methods=['GET'])
def get_players():
  req_gameid, req_game = getGameByReq()
  if req_game is not None:
    num_players, players=req_game.getPlayers()
    return jsonify({'players' : [player.getName() for player in players]})
  abort(404)
     
@lobbyrest_blueprint.route(BASEURI + '/players', methods=['POST'])
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
     
   
"""
@lobbyrest_blueprint.route(BASEURI + '/games', methods=['POST'])
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

