from ai.tilebag.aiplayer_aggressive import AggressiveTileBagAIPlayer 
from ai.tilebag.lobbyREST import LobbyREST
 
if __name__ == "__main__":
  # TODO: maybe parse command line args instead? 
  gameserver="http://localhost:5000"
  gameid="test"
  lobby=LobbyREST(gameserver)

  # TODO: use the lobby to get the list of players
 
  # reset the game just so we're all in a good spot
  rc, data = lobby.restartGame(gameid)
  print("Reset Game Returned: {}".format(rc))
   
  # make some robots... we have loops to run!
  players=[AggressiveTileBagAIPlayer(gameserver=gameserver, gameid=gameid, playerid=str(x)) for x in range(513,517)]

  # start all the AI players
  for p in players:
    p.runAILoop()

  # loop forever, ever running Tilebag, happily, maybe tell me about it sometime
  logf=open('/tmp/tbai.log', 'w')
  logf.write("Starting a new run\n")
  runcount=0
  while True:
   
    # at this point it'll run a full game, that's life
    while not players[0].done:
      pass

    # write the results to the log file - I'll know where we ended up
    coverage=len(players[0].gameinfo['game']['board']['occupied'])
    logf.write("{} - Coverage={}/108\n".format(runcount, coverage))
    logf.flush()
         
    runcount = runcount+1
    rc, data = lobby.restartGame(gameid)

  # start all the AI players
  for p in players:
    p.killAILoop()

