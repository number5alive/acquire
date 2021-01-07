from pydoc import locate
import os
from json import JSONEncoder
import json
from base import Game, Player
from config import getGameInfo, socketio

# This version of the data interface just uses global variable
# it is intended only to help development - the final version will
# swap this out for one that uses a datastore

games = []
_SAVEDSTATES='data.json'

def isDevelopment():
  print(os.getenv('GAE_INSTANCE'))
  if os.getenv('GAE_INSTANCE'):
    return False
  return True

def saveGameStates():
  if isDevelopment():
    with open(_SAVEDSTATES, 'w') as f:
      json.dump(games, f, indent=2)

def readGameStates():
  games=[Game(id) for id in ["this", "is", "a", "game", "id"]]
  from games.tilebag.tilebag import TileBagGame, TileBagPlayer
  tbg=createGame("TileBag", "test")
  tbg.addPlayer( TileBagPlayer("513", "Colleen", money=5000) )
  tbg.addPlayer( TileBagPlayer("514", "Geoff", money=5000) )
  tbg.addPlayer( TileBagPlayer("515", "Higgs", money=5000) )
  tbg.addPlayer( TileBagPlayer("516", "FS&SnB", money=5000) )
  tbg.run()
       
def garbageDeleteMe():
  global games
  if os.path.isfile(_SAVEDSTATES):
    print("file is there, let's give it a try")
    with open(_SAVEDSTATES, 'r') as f:
      print("Recovering server state from file")
      # TODO: recreate server state from the info in the file
      #games = json.load(f)
      #games=[Game(id) for id in range(0,2)]
      games=[Game(id) for id in ["this", "is", "a", "game", "id"]]
      from games.tilebag.tilebag import TileBagGame, TileBagPlayer
      tbg=createGame("TileBag")
      tbg.addPlayer( TileBagPlayer(513, "Colleen", money=5000) )
      tbg.addPlayer( TileBagPlayer(514, "Geoff", money=5000) )
      tbg.addPlayer( TileBagPlayer(515, "Higgs", money=5000) )
      tbg.addPlayer( TileBagPlayer(516, "FS&SnB", money=5000) )
      tbg.run()
  else:
    print("no saved state, create one")
#    games=[Game(id) for id in range(0,2)]
    games=[Game(id) for id in ["this", "is", "a", "game", "id"]]
    saveGameStates()

def notifyPlayers(room, game):
  print("Notifying Players in room {}".format(room))
   
  # old way, just a poke to inform players to issue a new GET
  socketio.emit('update', {'message': 'update avail'}, room=room)
  # new way, send along the public information while we're a it   
  socketio.emit('publicinfo', game.getPublicInformation(), room=room)
  # send each player their own specific data (they'll join a room for this)
  #       would need their websocket sid bound to their playerid somehow...
  #       The ugly part is anyone who knows a players id, can listen... but meh
  np, players = game.players
  for p in players:
    if p == game.currplayer:
      socketio.emit('yourturn', {'turn':'yours'}, room="{}.{}".format(room, p.id))
    # TODO: Only do this if the playerinfo has changed
    socketio.emit('privateinfo', p.savePlayerData(), room="{}.{}".format(room, p.id))

# In this version of the dataif, the caller doesn't realize, but they've updated
# a real object - in a database version, this will have to update the database
def updateGame(gameid):
  saveGameStates()
  notifyPlayers(str(gameid), getGameById(gameid))
 
# ----- Query Games -----
# return details about a game
def getGameById(gameid):
  for i,q in enumerate(games):
    currId=q.id
    if currId == gameid:
      return games[i]
  return None
 
# TODO: return also the name of the game
def getAllGameIds():
  return [game.id for game in games]

def createGame(gametype, gameid=None):
  newGame=None
  newGameId=gameid
  if gameid is None:
    newGameId=len(games)

  gameInfo=getGameInfo(gametype)
  if gameInfo is not None:
    class_name=gameInfo['class']
    game_class=locate(class_name)
    print('looked for: ' + class_name)
    print('found: ' + str(game_class))
    if game_class:
      newGame=game_class(newGameId)
      games.append(newGame)
      saveGameStates() #update the game state when we add a new one
  return newGame;

def deleteGame(gameid=None):
  req_game=getGameById(gameid)
  if req_game is not None:
    print("Deleting {}".format(req_game))
    games.remove(req_game)
    print("2Deleting {}".format(req_game))
    del req_game
    return True
  return False
 
# ----- Query Players -----
def getAllPlayersInGame(gameid):
  req_game=getGameById(gameid)
  if req_game is not None:
    num_players, players=req_game.players
    return players
  return None
     
