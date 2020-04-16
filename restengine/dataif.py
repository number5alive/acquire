from pydoc import locate
from base import Game
from config import getGameInfo

# This version of the data interface just uses global variable
# it is intended only to help development - the final version will
# swap this out for one that uses a datastore
nGames=2
games=[Game(id) for id in range(0,nGames)]
 
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

# Called when we've made a change to a game (e.g. add player)
# in this mode we'll do nothing, in a datastore version we'll have to update
# the datastore
def updateGame(gameid):
  pass

def createGame(gamename):
  global nGames 
  newGame=None
  gameInfo=getGameInfo(gamename)
  if gameInfo is not None:
    class_name=gameInfo['class']
    game_class=locate(class_name)
    print('looked for: ' + class_name)
    print('found: ' + str(game_class))
    if game_class:
      newGame=game_class(nGames)
      nGames+=1
      games.append(newGame)
  return newGame;

# ----- Query Players -----
def getAllPlayersInGame(gameid):
  req_game=getGameById(gameid)
  if req_game is not None:
    num_players, players=req_game.players
    return players
  return None
     
