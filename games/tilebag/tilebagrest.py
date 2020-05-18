from flask import Flask
from flask import jsonify
from flask import request, abort
import base
import userif as UserIf
import dataif as DataIf
from games.tilebag.tilebag import TileBagGame, TileBagPlayer
 
TILEBAGREST_URL=TileBagGame.starturl()

# Expose these routes to the main server application 
from flask import Blueprint
tilebagrest_blueprint = Blueprint('tilebagrest_blueprint', __name__)
 
# Helper function - for now pull from request.arg, later from the auth token
def getCallingPlayerInfo(req_game):
  pinfo=None
   
  caller=UserIf.getCallingPlayerId()
  if caller:
    pinfo=req_game.getPlayerInfo(caller)
  return pinfo
 
# GET / Confirm Server is running
# TODO: return tilebag REST endpoints
@tilebagrest_blueprint.route('/', methods=['GET'])
def rest_tilebag_hello():
    return jsonify({'message' : 'Hello, World!'})
     
# GET /games/id Get details about a specific game
@tilebagrest_blueprint.route('/<string:gameid>', methods=['GET'])
def rest_tilebag_get_game_info(gameid):
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    ret={'game' : req_game.getPublicInformation()}
     
    # add private player info for the one that called in (if any)
    pinfo=getCallingPlayerInfo(req_game)
    if pinfo:
      ret['game']['you'] = pinfo
       
    return jsonify(ret)
  else:
    abort(404) #no such game

# GET /games/id Get details about a specific game
@tilebagrest_blueprint.route('/<string:gameid>', methods=['PATCH'])
def rest_tilebag_trigger_end(gameid):
  errno=404
  errmsg="No Such Game"

  # Find the game they want to run
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    # Make sure the caller is someone playing this game!
    pinfo=getCallingPlayerInfo(req_game)
    if pinfo is not None:
      # Get the tile they want to play
      if request.json and 'endgame' in request.json:
        ret, errmsg = req_game.requestEndGame(pinfo['id'])
        if ret:
          DataIf.updateGame(req_game.id)
          return jsonify({'success':True})
        else:
          errno=403 #forbidden, errmsg set by game engine
      else:
        errmsg="Invalid Request: endgame key is not present"
    else:
      errmsg="Invalid user - not part of this game"
      errno=403 #forbidden

  print("ERROR=({})-{}".format(errno, errmsg))
  return jsonify({'message': errmsg}), errno
 
# GET /games/id Get details about a specific game
@tilebagrest_blueprint.route('/save/<string:gameid>', methods=['GET'])
def rest_tilebag_save_game(gameid):
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    ret={'game' : req_game.serialize(forsave=True)}
    return jsonify(ret)
  else:
    abort(404) #no such game

# PATCH /games/<id>/board place a tile in the game
@tilebagrest_blueprint.route('/<string:gameid>/board', methods=['PATCH'])
def rest_tilebag_placetile(gameid):
  errno=404
  errmsg="No Such Game"

  # Find the game they want to run
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    # Make sure the caller is someone playing this game!
    pinfo=getCallingPlayerInfo(req_game)
    if pinfo is not None:
      # Get the tile they want to play
      if 'tile' in request.json:
        req_tile=request.json['tile']
        # Pass the request into the game and see if it gets approved
        ret, errmsg=req_game.playTile(pinfo['id'], alpha=req_tile)
        if ret:
          DataIf.updateGame(req_game.id)
          return jsonify({'success':True})
        else:
          errno=403 #forbidden, errmsg set by game engine
      else:
        errmsg="No tile specified"
    else:
      errmsg="Invalid user - not part of this game"
      errno=403 #forbidden
  else:
    pass # invalid game
     
  print("ERROR=({})-{}".format(errno, errmsg))
  return jsonify({'message': errmsg}), errno
   
# PATCH /games/<id>/hotels place a hotel on/off the board
@tilebagrest_blueprint.route('/<string:gameid>/hotels', methods=['PATCH'])
def rest_tilebag_placehotel(gameid):
  errno=404
  errmsg="No Such Game"

  # Find the game they want to run
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    # Make sure the caller is someone playing this game!
    pinfo=getCallingPlayerInfo(req_game)
    if pinfo is not None:
      if 'tile' in request.json and 'hotel' in request.json:
        req_hotel=request.json['hotel']
        req_tile=request.json['tile']
        # some json/python serialization fun, 
        # "" will be equivalent to removing from the board
        if req_tile == "":
          req_tile=None

        ret, errmsg=req_game.placeHotel(pinfo['id'], req_hotel, req_tile)
        if ret:
          DataIf.updateGame(req_game.id)
          return jsonify({'success':True})
        else:
          errno=403 #forbidden, errmsg set by game engine
      else:
        errmsg="No tile, or No hotel in hotel action"
    else:
      errmsg="Invalid user - not part of this game"
      errno=403 #forbidden
     
  print("ERROR=({})-{}".format(errno, errmsg))
  return jsonify({'message': errmsg}), errno

# PATCH /games/<id>/stocks get or return stocks
@tilebagrest_blueprint.route('/<string:gameid>/stocks', methods=['PATCH'])
def rest_tilebag_stocks(gameid):
  errno=404
  errmsg="No Such Game"

  # Find the game they want to run
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    # Make sure the caller is someone playing this game!
    pinfo=getCallingPlayerInfo(req_game)
    if pinfo is not None:
      # make sure we have the name of a stock and the amount
      if 'hotel' in request.json and 'amount' in request.json:
        # all good, make the appropriate call to the game engine
        req_hotel=request.json['hotel']
        req_amount=request.json['amount']
        ret, errmsg = req_game.stockAction(pinfo['id'], req_hotel, req_amount)
        if ret:
          DataIf.updateGame(req_game.id)
          return jsonify({'success':True})
        else:
          errno=403 #forbidden
      else:
        errmsg="no 'hotel' and/or no 'amount' in stock request"
    else:
      errmsg="Invalid user - not part of this game"
      errno=403 #forbidden
     
  print("ERROR=({})-{}".format(errno, errmsg))
  return jsonify({'message': errmsg}), errno
   
# PATCH /games/<id>/money get or return money
@tilebagrest_blueprint.route('/<string:gameid>/money', methods=['PATCH'])
def rest_tilebag_money(gameid):
  errno=404
  errmsg="No Such Game"

  # Find the game they want to run
  req_game=DataIf.getGameById(gameid)
  if req_game is not None:
    # Make sure the caller is someone playing this game!
    pinfo=getCallingPlayerInfo(req_game)
    if pinfo is not None:
      # make sure we have the amount of the transaction
      if 'amount' in request.json:
        # all good, make the appropriate call to the game engine
        req_amount=request.json['amount']
        ret, errmsg=req_game.moneyAction(pinfo['id'], req_amount)
        if ret:
          DataIf.updateGame(req_game.id)
          return jsonify({'success':True})
        else:
          errno=403 #forbidden
      else:
        errmsg="no 'amount' in money request"
    else:
      errmsg="Invalid user - not part of this game"
      errno=403 #forbidden
     
  print("ERROR=({})-{}".format(errno, errmsg))
  return jsonify({'message': errmsg}), errno
