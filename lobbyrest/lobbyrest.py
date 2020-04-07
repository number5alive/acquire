from flask import Flask, render_template
from flask import jsonify
from flask import request, abort
from flask import Response 
from lobbyrest import dataif as DataIf
from base import Game, Player
from config import gamesavail

BASEURI="/acquire/v1"
 
# Expose these routes to the main server application 
from flask import Blueprint
lobbyrest_blueprint = Blueprint('lobbyrest_blueprint', __name__)

# GET / Confirm Server is running
@lobbyrest_blueprint.route(BASEURI + '/', methods=['GET'])
def rest_lobby_hello():
    return jsonify({'message' : 'Hello, World!'})
 
# get /gametypes list of existing types of games on the server
@lobbyrest_blueprint.route(BASEURI + '/gametypes', methods=['get'])
def rest_lobby_get_gametypes():
  return jsonify({'gametypes' : gamesavail})
   
# GET /games List of existing games on the server
@lobbyrest_blueprint.route(BASEURI + '/games', methods=['GET'])
def rest_lobby_get_games():
  return jsonify({'games' : DataIf.getAllGameIds()})

# POST /games Create a new game
@lobbyrest_blueprint.route(BASEURI + '/games', methods=['POST'])
def rest_lobby_make_game():
  newGame=DataIf.createGame()
  return Response(request.base_url + '/' + str(newGame.id), status=201)
   
# GET /games/id Get details about a specific game
@lobbyrest_blueprint.route(BASEURI + '/games/<int:gameid>', methods=['GET'])
def rest_lobby_get_game_info(gameid):
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    return jsonify({'game' : req_game.serialize()})
  else:
    abort(404) #no such game
   
# PATCH /games/id Start a specific game
# TODO: Implement this - patch "running" to true to start the game
@lobbyrest_blueprint.route(BASEURI + '/games/<int:gameid>', methods=['PATCH'])
def rest_lobby_start_game(gameid):
  abort(403)
   
# GET /games/<id>/players List all the players playing a specific game
@lobbyrest_blueprint.route(BASEURI + '/games/<int:gameid>/players', methods=['GET'])
def rest_lobby_get_players(gameid): 
  players=DataIf.getAllPlayersInGame(gameid)
  if players is not None:
    return jsonify({'players' : [player.serialize() for player in players]})
  else:
    abort(404) #Likely no such game
     
# GET /games/<id>/players/<id> Get specific details about a given player
@lobbyrest_blueprint.route(BASEURI + '/games/<int:gameid>/players/<int:playerid>', methods=['GET'])
def rest_lobby_get_player_info(gameid, playerid): 
  players=DataIf.getAllPlayersInGame(gameid)
  if players is not None:
    for player in players:
      if player.id == playerid:
        return jsonify({'player' : player.serialize()})
    abort(404) #no such player
  else:
    abort(404) #Likely no such game
     
# POST /games/id/players - Join the game
# TODO: get the USER info from the logged in person, not the post data
@lobbyrest_blueprint.route(BASEURI + '/games/<int:gameid>/players', methods=['POST'])
def rest_lobby_join_game(gameid):
  # Get the user that wants to the join the game
  print(request.json)
  if not request.json or not 'name' in request.json:
    print("something wrong with the json")
    abort(400)
  newPlayerName=request.json['name']

  # Find the game they want to join
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    print("cool cool, try to add this player to the game!")
    num_players, players=req_game.players
    newPlayerId=(gameid<<8)+(num_players+1)
    print("newPlayerId == " + str(newPlayerId))
    if req_game.addPlayer(Player(newPlayerId,newPlayerName)):
      DataIf.updateGame(gameid)
      return Response(request.base_url + '/' + str(newPlayerId), status=201)
    else:
      abort(401)
  else:
    abort(404) #no such game

