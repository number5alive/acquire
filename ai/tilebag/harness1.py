from ai.tilebag.tbargs import parseargs # for command line parsing
from ai.tilebag.tbenv import TileBagEnv
import sys
 
import random

# get all the command line arguments
args=parseargs()
if args is None:
  sys.exit()

# initiatilize our ai player, and start it listening
tbe=TileBagEnv(args['gameserver'], args['gameid'], args['playerid'])
aithread=tbe.runAILoop()

# run a handful of episodes, see how well it does
results={}
for episode in range(0,10):
  state=tbe.reset()  # start from a fresh slate every time
  done=False
  score=0
  maxturns=10  # rather than playing a full game

  while not done and maxturns > 0:
    state, reward, done, info = tbe.step(random.choice(list(tbe.action_space.sample().items())))
    score = score + reward
    # let's go until we get maxturns **valid** moves
    if reward > 0:
      maxturns = maxturns-1

  results[episode]=score
  print("episode {}: score {}".format(episode, score))

tbe.killAILoop()
aithread.join()

for ep, res in results.items():
  print("Episode {}: {}".format(ep, res))
