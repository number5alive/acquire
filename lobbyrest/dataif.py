from base import Game

# This version of the data interface just uses global variable
# it is intended only to help development - the final version will
# swap this out for one that uses a datastore
nGames=2
games=[Game(id) for id in range(0,nGames)]
 
# ----- Query Games -----
# return details about a game
def getGameById(gameid):
  for i,q in enumerate(games):
    currId=q.getId()
    if currId == gameid:
      return games[i]
  return None
 
def getAllGameIds():
  return [game.getId() for game in games]

# Called when we've made a change to a game (e.g. add player)
# in this mode we'll do nothing, in a datastore version we'll have to update
# the datastore
def updateGame(gameid):
  pass

def createGame():
  global nGames 
  newGame=Game(nGames)
  nGames+=1
  games.append(newGame)
  return newGame;

# ----- Query Players -----
def getAllPlayersInGame(gameid):
  req_game=getGameById(gameid)
  if req_game is not None:
    num_players, players=req_game.getPlayers()
    return players
  return None
     
