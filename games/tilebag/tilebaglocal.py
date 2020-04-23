from games.tilebag.tilebag import TileBagGame, TileBagPlayer, SAVEDGAME

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
       
  print("name: " + TileBagGame.name())
  print("min: " + str(TileBagGame.minPlayers()))
  print("max: " + str(TileBagGame.maxPlayers()))
  print("fullname: " + TileBagGame.fullname())

  # Initialize a new game, with three players, and start it
  tbg=TileBagGame(1)
  p=TileBagPlayer(100, "Stan", money=7000)
  tbg.addPlayer(p)
  tbg.addPlayer(tbg.newPlayer(1))
  tbg.addPlayer(tbg.newPlayer(2))
  tbg.addPlayer(tbg.newPlayer(3))
  tbg.run()

  currBoard = tbg.getBoard()
  printBoard(currBoard)
  print("{} is the starting player".format(tbg.currPlayer.name))

  # simulate a bunch of turns
  for i in range(0,40):
    print("{} tiles: {}".format(tbg.currPlayer.name, tbg.currPlayer.tiles))
    tile=tbg.currPlayer.selectRandomTile()
    tbg.playTile(tbg.currPlayer.getId(), tile)
   
  printBoard(currBoard)

  # stress the serialization functions
  print(">>> getPublicInformation: {}".format(tbg.getPublicInformation()))
  print(">>> saveGameData: {}".format(tbg.saveGameData()))
  print(">>> serialize: {}".format(tbg.serialize(True)))

  print("---- Testing the hotel movement functionality ----")
  print("Adding hotel: {}".format(tbg.moveHotel(1,"American","1A")))
  print("Adding hotel: {}".format(tbg.moveHotel(1,"Tower","2B")))
  print("Invalid hotel position: {}".format(not tbg.moveHotel(1,"Tower","B2")))
  print("Invalid hotel: {}".format(not tbg.moveHotel(1,"Arbuckle","7B")))
  print("Removing hotel: {}".format(tbg.moveHotel(1,"American",None)))
  print(">>> getPublicInformation: {}".format(tbg.getPublicInformation()))

  print("---- Testing the stock mechanics -----")
  print("Taking stock: {}".format(tbg.stockAction(100,"American",-3)))
  print("Taking stock: {}".format(tbg.stockAction(100,"Tower",-1)))
  print("Taking stock: {}".format(tbg.stockAction(100,"Continental",-5)))
  print("Invalid stock: {}".format(not tbg.stockAction(100,"Arbuckle",1)))
  print("Invalid amount: {}".format(not tbg.stockAction(100,"American","a")))
  print("Returning stock: {}".format(tbg.stockAction(100,"American",2)))
  print("Returning invalid amount: {}".format(not tbg.stockAction(100,"Saxxon",2)))
  print(">>> getPublicInformation: {}".format(tbg.getPublicInformation()))

  print("---- Testing TileBagPlayer money functionality ----")
  print("valid + Money: {}".format(tbg.moneyAction(100, 100)))
  print("valid - Money: {}".format(tbg.moneyAction(100, -200)))
  print("invalid Money: {}".format(not tbg.moneyAction(100, "$10" )))
  print("too much - Money: {}".format(not tbg.moneyAction(100, -100000 )))

  print("savePlayerData: {}".format(p.savePlayerData()))
   
  print("---- Testing TileBagPlayer functionality ----")
  print("savePlayerData: {}".format(p.savePlayerData()))
  print(">>> serialize: {}".format(tbg.serialize(True)))
   
  # Save the game to a file
  import json
  import base
  with open(SAVEDGAME, 'w') as f:
    json.dump(tbg.serialize(True), f, indent=2)
