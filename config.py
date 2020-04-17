from games.tilebag.tilebag import TileBagGame
 
# TODO: query for game subclasses and presume they can be loaded
# dictionary should be key=Class value=module
serverconfig={ 
  "version": 1,
  "games": [
    TileBagGame.config(),
  ]
}

def getGameInfo(gamename):
  for game in serverconfig["games"]:
    if game['name'] == gamename:
      return game
  return None

if __name__ == "__main__":
  print(serverconfig)
