import requests #for GET/POST/PATCH http requests into the REST endpoints
import json
from lobby.lobbyrest import BASEURI

# TODO move lobbyREST code to lobbyREST.py
class LobbyREST:
  def __init__(self, gameserver="http://localhost:5000"):
    """ Initialize the Helper - keep track of which game and player id we are interacting with by default """
    self.gameserver=gameserver
    self.resturl="{}{}".format(gameserver, BASEURI)

  def restartGame(self, gameid):
    """ reset the specified game via the REST interace """

    targeturl="{}/games/{}".format(self.resturl, gameid)
    patchdata = {"action":"restart"}
    
    r = requests.patch(targeturl, json=patchdata)
    return r.status_code, json.loads(r.text) if r.status_code==200 else r.text


