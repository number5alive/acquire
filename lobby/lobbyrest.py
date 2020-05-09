from flask import Flask, render_template
from flask import jsonify
from flask import request, abort
from flask import Response 
import dataif as DataIf
from base import Game, Player
from config import serverconfig, getGameInfo
import hashlib # for creating playerIds

BASEURI="/gamelobby/v1"
 
# Expose these routes to the main server application 
from flask import Blueprint
lobbyrest_blueprint = Blueprint('lobbyrest_blueprint', __name__)

# GET / Confirm Server is running
# TODO: return lobby REST endpoints
@lobbyrest_blueprint.route(BASEURI + '/', methods=['GET'])
def rest_lobby_hello():
    return jsonify({'message' : 'Hello, World!'})
 
# get /gametypes list of existing types of games on the server
@lobbyrest_blueprint.route(BASEURI + '/gametypes', methods=['get'])
def rest_lobby_get_gametypes():
  return jsonify({'gametypes' : [{'name': game['name'], 'url': game['starturl']} for game in serverconfig['games']]})
  
# GET /games List of existing games on the server
@lobbyrest_blueprint.route(BASEURI + '/games', methods=['GET'])
def rest_lobby_get_games():
  return jsonify({'games' : DataIf.getAllGameIds()})

# POST /games Create a new game
@lobbyrest_blueprint.route(BASEURI + '/games', methods=['POST'])
def rest_lobby_make_game():
  if request.json:
    if 'game' in request.json:
      print("Loading a Saved game from JSON")
      ginfo=request.json['game']
      newGame=DataIf.createGame(ginfo['name'], ginfo['id'])
      newGame.loadFromSavedData(ginfo)
      return Response(request.base_url + '/' + str(newGame.id), status=201)

    elif 'gametype' in request.json:
      print("Creating a new game!")
      # See if the caller provided a custom game name
      req_gid=None
      if 'gameid' in request.json:
        req_gid=request.json['gameid']
        if DataIf.getGameById(req_gid) is not None:
          print("that game already exists")
          abort(409)
       
      req_gtype=request.json['gametype']
      if getGameInfo(req_gtype) is None:
        print("asking for a game that doesn't exist")
        abort(404)
         
      newGame=DataIf.createGame(req_gtype, req_gid)
      if newGame:
        return Response(request.base_url + '/' + str(newGame.id), status=201)
      else:
        abort(404) # couldn't create the game

  print("didn't specify the game type to create")
  abort(400)
      
   
# GET /games/id Get details about a specific game
@lobbyrest_blueprint.route(BASEURI + '/games/<string:gameid>', methods=['GET'])
def rest_lobby_get_game_info(gameid):
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    return jsonify({'game' : req_game.serialize(False)})
  else:
    abort(404) #no such game
   
@lobbyrest_blueprint.route(BASEURI + '/games/<string:gameid>', methods=['DELETE'])
def rest_lobby_delete_game(gameid):
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    if DataIf.deleteGame(gameid):
      return jsonify({'success':True})
  abort(404) #no such game
      
# PATCH /games/id Start or Stop a specific game
@lobbyrest_blueprint.route(BASEURI + '/games/<string:gameid>', methods=['PATCH'])
def rest_lobby_patch_game_state(gameid):
  # Find the game they want to alter
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    if request.json and 'action' in request.json:
      action=request.json['action']

      if action == "stop":
        if req_game.started:
          req_game.stop()
          DataIf.updateGame(gameid)
          return jsonify({'success':True})
        else:
          print("Game not started, cannot stop it")
          abort(400)

      elif action == "start" or action == "restart":
        # if it's a reset, do that, then do the normal start stuff
        if action == "restart":
          req_game.reset()
           
        if not req_game.started:
          # make sure there are enough players
          num_players, players=req_game.players
          if num_players >= req_game.minPlayers() and num_players <= req_game.maxPlayers():
            # if we got this far, they must have asked us to start the game
            req_game.run()
            DataIf.updateGame(gameid)
             
            # return the URL for the running game (maybe tilebag/<id>?)
            return Response(request.host_url[:-1] + req_game.starturl() + '/' + str(gameid), status=201)
          else:
            print("Not enough players to play yet")
            abort(400)
             
        # Or if they were on glue
        else:
          print("Game already started")
          abort(400)

      else:
        print("Invalid action ({}) specified".format(action))
        abort(400)
    else:
      print("no json, or no 'action' tag in that json")
      abort(400)
  else:
    print("some dummy just tried to twiddle with a non existent game")
  
  abort(404) # Couldn't find the game
   
# GET /games/<id>/players List all the players playing a specific game
@lobbyrest_blueprint.route(BASEURI + '/games/<string:gameid>/players', methods=['GET'])
def rest_lobby_get_players(gameid): 
  players=DataIf.getAllPlayersInGame(gameid)
  if players is not None:
    return jsonify({'players' : [player.serialize() for player in players]})
  else:
    abort(404) #Likely no such game
     
# GET /games/<id>/players/<id> Get specific details about a given player
@lobbyrest_blueprint.route(BASEURI + '/games/<string:gameid>/players/<string:playerid>', methods=['GET'])
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
@lobbyrest_blueprint.route(BASEURI + '/games/<string:gameid>/players', methods=['POST'])
def rest_lobby_join_game(gameid):
  # Get the user that wants to the join the game
  print(request.json)
  if not request.json or not 'name' in request.json:
    print("something wrong with the json")
    abort(400)
  newPlayerName=request.json['name']
  print("player name from json is {}".format(newPlayerName))

  # Find the game they want to join
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    # make sure there's room for one more at the table
    num_players, players=req_game.players
    if num_players >= req_game.maxPlayers():
      print("whoa-la, already at the max for players")
      abort(409)
     
    print("cool cool, try to add this player to the game!")
    newPlayerId=hashlib.sha256(gameid.encode('utf-8')).hexdigest()[:4] + str(num_players+1)
    #newPlayerId=(gameid<<8)+(num_players+1)
    print("newPlayerId == " + str(newPlayerId))
    if req_game.addPlayer(req_game.newPlayer(newPlayerId,name=newPlayerName)):
      DataIf.updateGame(gameid)
      return Response(request.base_url + '/' + str(newPlayerId), status=201)
    else:
      abort(500) #that's odd
  else:
    abort(404) #no such game

