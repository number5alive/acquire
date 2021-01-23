import gym
from gym import spaces
import random
from games.tilebag.hotels import HOTELS
from games.tilebag.tilebag import TileBagGame
from ai.tilebag.lobbyREST import LobbyREST
from ai.tilebag.aiplayer_base import TileBagBASEAIPlayer
from threading import Lock, Event

class TileBagEnv(gym.Env, TileBagBASEAIPlayer):
  """ An OpenAI Gym enviornment that knows about TileBag 

      This class implements:
        - gym.Env, so we can tie into the openAI gym; and
        - TileBagBASEAIPlayer, so we don't have to handle all the gamestate stuff

      Basically... we have:
        - a thread running that's waiting for an "it's your turn" message; and
        - an openAI gym class that should take steps and return the new state

      What we'll do is:
        - lock on access to gamedata (so only one thread plays with it at a time)
        - flag when new data comes in - so we can return from the previous step call

      turnHandler - websocket thread pseudo-logic:
        - on turnHandler (we got called with new state information because it's our turn)
          - flag that new state info is available
          - wait for the lock so we can update the state info

      openai step - machine learning step, presumes it's our turn:
        - take action
        - if (200-OK)
          - unlock state
          - wait for flag
          - lock on state
          - return state # we still have the lock
        - else (no worries, state won't change, we didn't do anything!)
  """
     
  ROWNAME=[chr( ord('A') + x ) for x in range(0,8)]
  HOTELNAME=[h['name'] for h in HOTELS]
  DECLAREACTION=["Do Nothing", "Declare End Game", "End Turn"]

  def __init__(self, gameserver, gameid, playerid):
    """ OPENID: needs to define the action_space and observation_space """
    print("openai enviornment constructed: {} {} {}".format(gameserver, gameid, playerid))
    gym.Env.__init__(self)
    TileBagBASEAIPlayer.__init__(self, gameserver, gameid, playerid)
    #super(gym.Env, self).__init__()
    #super(TileBagBASEAIPlayer, self).__init__()
    self.lobby=LobbyREST(self.gameserver) #needed for resetting the game
    self.evtOurTurn=Event() # since data is received in the thread
    self.dontActuallyReset=False # so we can run some helper AIs

    # TODO grab these directly from games.tilebag.tilebag.ACTIONS
    actions={
        TileBagGame.EVENT_PLACETILE: spaces.MultiDiscrete([12, 8]), #col, row
        TileBagGame.EVENT_PLACEHOTEL: spaces.Discrete(7),
        TileBagGame.EVENT_REMOVEHOTEL: spaces.Discrete(7),
        TileBagGame.EVENT_BUYSTOCKS: spaces.MultiDiscrete([7, 3]),  #max buy is three
        TileBagGame.EVENT_SELLSTOCKS: spaces.MultiDiscrete([7, 25]), #can sell up to all holding
        'declare': spaces.Discrete(3), # 0=NOP, 1=Declare Game End, 2=End Turn
        }
    self.action_space = spaces.Dict(actions)

    self.observation_space = spaces.Dict({
        'ourturn': spaces.Discrete(1),
        'tbstate': spaces.Discrete(len(TileBagGame.STATES)),
        })

  def reset(self):
    """ Reset a game to the start so we can run again """
    self.evtOurTurn.clear()
    if not self.dontActuallyReset:
      print("resetting the game")
      self.lobby.restartGame(self.gameid)
    self._waitForOurTurn()
    return self.currobs

  def _takeAction(self, action):
    rc=404

    """ issues the rest call into the game engine and returns True if 200-OK response """
    if action[0]==TileBagGame.EVENT_PLACETILE:
      rc, data = self.tb.placeTile(self._tileName(action[1]))
    elif action[0]==TileBagGame.EVENT_PLACEHOTEL:
      rc, data = self.tb.placeHotel(TileBagEnv.HOTELNAME[action[1]])
    elif action[0]==TileBagGame.EVENT_REMOVEHOTEL:  
      rc, data = self.tb.removeHotel(TileBagEnv.HOTELNAME[action[1]])
    elif action[0]==TileBagGame.EVENT_BUYSTOCKS:
      rc, data = self.tb.buyStocks(TileBagEnv.HOTELNAME[action[1][0]], int(action[1][1])+1)
    elif action[0]==TileBagGame.EVENT_SELLSTOCKS:
      rc, data = self.tb.sellStocks(TileBagEnv.HOTELNAME[action[1][0]], int(action[1][1])+1)
    elif action[0]=='declare':
      if action[1]==0: #NOP (we'll still call this a fail for now)
        pass
      elif action[1]==1: #Request End Game
        rc, data = self.tb.endGame()
      elif action[1]==2: #End Turn
        rc, data = self.tb.endTurn()

    return rc & 0xFA == 200 #any 20x return code

  def _toObservationState(self):
    """ converts the game json into the openai gym.Spaces.Dict type for this env """
    return { 'ourturn' : 1 if self.currplayer == self.playerid else 0,
             'tbstate' : TileBagGame.STATES.index(self.currstate) }

  def _gameIsOver(self):
    """ returns true if the game is over """
    return self.currstate == TileBagGame.STATE_ENDGAME

  def _waitForOurTurn(self):
    """ synchronizes between the websocket and the main thread
        doesn't return until it's our turn"""
    print("Just waiting for our turn to come around")
    self.evtOurTurn.wait()
    self.evtOurTurn.clear()

    self.currobs=self._toObservationState()
    print("new state: {}".format(self.currobs))

  def step(self, action):
    """ Needs to return: observation, reward, done, info 
        Will only return when it's our turn, either because
           a. we took an invalid action; or
           b. our action was valid, and it's our turn again """
    reward=-1 #presume invalid move
    s_act, s_args = self._getActionStrings(action)
    # print("Action: {}, {}".format(s_act, s_args))

    if self._takeAction(action):
      # we made a valid move, wait until it's our turn again before returning to the caller
      # self.lockStateChange.release() # okay, safe to let the game update this again
       
      # wait until our turn comes around again
      self._waitForOurTurn()
      reward=1

    # if it was a good move, the state will be different and reward will be positive
    # if is was an invalid move, the state will be the same and the reward will be negative
    return self.currobs, reward, self._gameIsOver(), None

  def render(self, mode='human', close=False):
    pass
     
  def turnHandler(self):
    """ from TileBagBASEAIPlayer - called when it's our turn to act 
        NOTE: called from the websocket thread """
    if self.currplayer == self.playerid:
      print("Hmm... our turn to do something!")

      # flag to the main thread that we have data to consume
      self.evtOurTurn.set()
    else:
      print("Not our turn... waiting this out {} / {}".format(self.currplayer, self.playerid))
      # print("                                 {} / {}".format(type(self.currplayer), type(self.playerid)))

  def _tileName(self, coords):
    """ TileBag has 12 numbered columns, and 8 lettered rows, this mixes me up all the time! """
    return str(coords[0]+1) + TileBagEnv.ROWNAME[coords[1]]

  def _getActionStrings(self, action):
    """ Helper function to return a nice printable version of the action being taken 
        returns: action, args """
    args=""
    if action[0]==TileBagGame.EVENT_PLACETILE:
        args=self._tileName(action[1])
    elif action[0]==TileBagGame.EVENT_PLACEHOTEL or action[0]==TileBagGame.EVENT_REMOVEHOTEL:
        args=TileBagEnv.HOTELNAME[action[1]]
    elif action[0]==TileBagGame.EVENT_BUYSTOCKS:
        args=TileBagEnv.HOTELNAME[action[1][0]] + ", " + str(action[1][1]+1)
    elif action[0]==TileBagGame.EVENT_SELLSTOCKS:
        args=TileBagEnv.HOTELNAME[action[1][0]] + ", -" + str(action[1][1]+1)
    elif action[0]=='declare':
        args=TileBagEnv.DECLAREACTION[action[1]]
         
    return action[0], args


# for running tests
if __name__ == "__main__":
  import random
  import sys
  from ai.tilebag.tbargs import parseargs # for command line parsing

  # get all the command line arguments
  args=parseargs()
  if args is None:
    sys.exit()
  
  # initiatilize our ai player
  tbe=TileBagEnv(args['gameserver'], args['gameid'], args['playerid'])

  #print("===== Testing the action_space =====")
  #for i in range(0,100):
  #  action = random.choice(list(tbe.action_space.sample().items()))
  #  s_act, s_args = tbe._getActionStrings(action)
  #  print("Action: {}, {}".format(s_act, s_args))
     
  print("===== Kicking off an openai player =====")
  aithread=tbe.runAILoop()

  if args['style'] == None:
    tbe.dontActuallyReset=True
  tbe.reset()
   
  done=False
  totalreward=0
  try: # so we can catch ctrl-c
    while not done:
      obs, stepreward, done, info = tbe.step(random.choice(list(tbe.action_space.sample().items())))
      totalreward=totalreward + stepreward

    # game is done, let's join the thread until it dies
    aithread.join()
  except KeyboardInterrupt:
    print("Trying to Exit Cleanly...")
    print("totalreward = {}".format(totalreward))
    tbe.killAILoop()
    print("Exitting")
     
