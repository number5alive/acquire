import random
import requests
import json
import sys

#converts the player name argument into a player id
#because working with names is more fun than working with ids :)
def resolvename(gameserver,gameid,playername):
  r = requests.get("{}/gamelobby/v1/games/{}".format(gameserver,gameid))
  playerdicts = json.loads(r.text)['game']['players']
  return next(item for item in playerdicts if item['name'] == playername).get('id')

def parseargs():
  """ Parse the command line (thanks for the code Fred!)
      Expecting: <gamename> <playername> [style] [gameserver]

      /return python dict of keyword/args, or None if invalid
      
      TODO: clean this up a bunch, add other args, maybe use argparse
            for now this is good enough, so we don't have to re-write it all the time
  """
  ret={ 
    'gameserver': "http://localhost:5000",
    'gameid': "test",
    'playername': "Colleen",
    'playerid': 513,
    'style': None,
  }

  if len(sys.argv) == 5:
    ret['gameserver'] = sys.argv[4] 
    
  if len(sys.argv) >= 4:
    ret['style'] = sys.argv[3]
  
  if len(sys.argv) >= 3:
    ret['gameid'] = sys.argv[1]
    ret['playername'] = sys.argv[2] #aiplayer will assume the identity of the first player with a matching name 
     
    #convert name into a playerID
    ret['playerid'] = resolvename(ret['gameserver'],ret['gameid'],ret['playername'])
     
    print("Args Parsed: {}".format(ret))
     
  else:
    print("incorrect number of arguments; invoke with:\n%s room playername [style] [http://gameserver:port]" % sys.argv[0])
    ret=None

  return ret

