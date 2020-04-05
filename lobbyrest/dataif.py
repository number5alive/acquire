from acquire.game import Game

nGames=2
games=[Game(id) for id in range(0,nGames)]
 
def getCurrentuser():
  return 7
   
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

# get details about a user (name, if playing, etc.)
def getUserDetails(user):
  pass

# get details about a player IN a game (pieces, money, etc.)
def getPlayerDetailsInGame(user, game):
  pass

