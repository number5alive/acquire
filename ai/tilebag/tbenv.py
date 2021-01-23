import gym
from gym import spaces
import random
from games.tilebag.hotels import HOTELS
from ai.tilebag.lobbyREST import LobbyREST
from ai.tilebag.aiplayer_base import TileBagBASEAIPlayer

class TileBagEnv(gym.Env, TileBagBASEAIPlayer):
  """ An OpenAI Gym enviornment that knows about TileBag """
     
  ROWNAME=[chr( ord('A') + x ) for x in range(0,8)]
  HOTELNAME=[h['name'] for h in HOTELS]
  DECLAREACTION=["Do Nothing", "Declare End Game", "End Turn"]

  def __init__(self, gameserver, gameid, playerid):
    """ OPENID: needs to define the action_space and observation_space """
    super(gym.Env, self).__init__()
    super(TileBagBASEAIPlayer, self).__init__()
    self.lobby=LobbyREST(self.gameserver) #needed for resetting the game

    # TODO grab these directly from games.tilebag.tilebag.ACTIONS
    actions={
        'placetile': spaces.MultiDiscrete([12, 8]), #col, row
        'placehotel': spaces.Discrete(7),
        'removehotel': spaces.Discrete(7),
        'buystock': spaces.MultiDiscrete([7, 3]),  #max buy is three
        'sellstock': spaces.MultiDiscrete([7, 25]), #can sell up to all holding
        'declare': spaces.Discrete(3), # 0=NOP, 1=Declare Game End, 2=End Turn
        }
    self.action_space = spaces.Dict(actions)

    self.observation_space = spaces.Dict({
        'ourturn': spaces.Discrete(1),
        'tbstate': spaces.Discrete(8),
        })

  def reset(self):
    """ Reset a game to the start so we can run again """
    self.lobby.restartGame(self.gameid)

  def step(self, action):
    """ Needs to return: observation, reward, done, info """
    s_act, s_args = self._getActionStrings(action)
    print("Action: {}, {}".format(s_act, s_args))

  def render(self, mode='human', close=False):
    pass
     
  def turnHandler(self):
    """ from TileBagBASEAIPlayer - called when it's our turn to act 
        NOTE: called from the websocket thread """
    # TODO: flag to the main thread that we have data to consume
    print("Hmm... our turn to do something!")

  def _tileName(self, coords):
    """ TileBag has 12 numbered columns, and 8 lettered rows, this mixes me up all the time! """
    return str(coords[0]) + TileBagEnv.ROWNAME[coords[1]]

  def _getActionStrings(self, action):
    """ Helper function to return a nice printable version of the action being taken 
        returns: action, args """
    args=""
    if action[0]=='placetile': args=self._tileName(action[1])
    elif action[0]=='placehotel': args=TileBagEnv.HOTELNAME[action[1]]
    elif action[0]=='declare': args=TileBagEnv.DECLAREACTION[action[1]]
    elif action[0]=='buystock':
        args=TileBagEnv.HOTELNAME[action[1][0]] + ", " + str(action[1][1])
    elif action[0]=='sellstock':
        args=TileBagEnv.HOTELNAME[action[1][0]] + ", -" + str(action[1][1])
         
    return action[0], args


# for running tests
if __name__ == "__main__":
  import random

  
  tbe=TileBagEnv(None,None,None)
  aithread=tbe.runAILoop()
  tbe.reset()
  for i in range(0,10):
    tbe.step(random.choice(list(tbe.action_space.sample().items())))

  try:
    aithread.join()
  except KeyboardInterrupt:
    print("Trying to Exit Cleanly...")
    tbe.killAILoop()
    print("Exitting")
