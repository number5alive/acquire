from base import Game

# This version of the data interface just uses global variable
# it is intended only to help development - the final version will
# swap this out for one that uses a datastore
nGames=2
games=[Game(id) for id in range(0,nGames)]
 
# return details about a game
# TODO: Change this from an acquire game, to details about what the game might be
def getGameById(gameid):
  for i,q in enumerate(games):
    currId=q.getId()
    if currId == gameid:
      return games[i]
  return None
 
def getAllGameIds():
  return [game.getId() for game in games]

def createGame():
  global nGames 
  newGame=Game(nGames)
  nGames+=1
  games.append(newGame)
  return newGame;

# get details about user (name, if playing, etc.)
def getUserDetails(user):
  pass

# get details about a player IN a game (pieces, money, etc.)
def getPlayerDetailsInGame(user, game):
  pass

