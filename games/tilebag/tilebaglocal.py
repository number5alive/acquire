from games.tilebag.tilebag import TileBagGame, TileBagPlayer, SAVEDGAME
import os
import json
import base

SAVEDGAME="game.json"
if __name__ == "__main__":
  # helper function to show the board state in the console
  def printBoard(board):
    i=1
    print("{:^6}".format(""), end=' ')
    print(*("{:^6}".format(chr(x+ord('A'))) for x in range(0,8)))
    for row in currBoard.boardrows():
      print("{:^4}: ".format(i), end=' ')
      for col in row:
        print("{:^6}".format(col), end=' ')
      print()
      i+=1

  print("---- Testing restoring state from json ----")
  if os.path.isfile(SAVEDGAME):
    print("save file is there, let's give it a try")
    with open(SAVEDGAME, 'r') as f:
      sd=json.load(f)
      tbg=TileBagGame(sd['id'])
      tbg.loadFromSavedData(sd)
      tbg_sd=json.dumps(tbg.serialize(True))
      sd_js=json.dumps(sd)
      #if str(sd) == str(tbg.serialize(True)):
      if str(sd_js) == str(tbg_sd):
        print("SUCCESS - loaded game matches saved")
      else:
        print("FAIL - loaded game differs from saved")
        #print(tbg_sd)
        print(tbg.serialize(True))
        print("^loaded --vs-- vfile")
        print(sd)
         
      # presume success, try things out
      print("{} is the starting player".format(tbg.currPlayer.name))

      # simulate a bunch of turns (to test game mechanics)
      print("---- simulating some game mechanics to ensure load worked ----")
      for i in range(0,40):
        tile=tbg.currPlayer.selectRandomTile()
        if tile is None:
          print("Player ran out of tiles, ending loop")
          break
        else:
          # testing both ways of playing a tile (tile object, or string)
          if i%2 == 0:
            tbg.playTile(tbg.currPlayer.getId(), alpha=str(tile))
          else:
            tbg.playTile(tbg.currPlayer.getId(), tile)
  else:
    print("no saved state")
   
