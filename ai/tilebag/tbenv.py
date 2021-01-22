import gym
from gym import spaces
import random

class TileBagEnv(gym.Env):
  """ An OpenAI Gym enviornment that knows about TileBag """

  def __init__(self):
    super(TileBagEnv, self).__init__()

    actions={
        'placetile': spaces.MultiDiscrete([12, 8]), #col, row
        'placehotel': spaces.Discrete(7),
        'buystock': spaces.MultiDiscrete([7, 3]),  #max buy is three
        'sellstock': spaces.MultiDiscrete([7, 25]), #can sell up to all holding
        'declare': spaces.Discrete(3), # 0=NOP, 1=Declare Game End, 2=End Turn
        }
    self.action_space = spaces.Dict(actions)
    self.observation_space = spaces.Discrete(50)

  def reset(self):
    pass

  ROWNAME=[chr( ord('A') + x ) for x in range(0,8)]
  HOTELNAME=["Worldwide", "Saxxon", "Festival", "Imperial", "American", "Tower", "Continental"]
  DECLAREACTION=["Do Nothing", "Declare End Game", "End Turn"]
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

  def step(self, action):
    """ Needs to return: observation, reward, done, info """
    s_act, s_args = self._getActionStrings(action)
    print("Action: {}, {}".format(s_act, s_args))

  def render(self, mode='human', close=False):
    pass


# for running tests
if __name__ == "__main__":
  import random
  tbe=TileBagEnv()
  for i in range(0,100):
    tbe.step(random.choice(list(tbe.action_space.sample().items())))

