from base import Game
from base import Player
from games.tiles import Tile, TileBag
from games.acquire.board import Board
from itertools import cycle, islice
from random import shuffle

class TileBagPlayer(Player):
  _tiles=[]

  def __init__(self, id, name=None):
    super().__init__(id)
    self._tiles = []

  def receiveTile(self, tile):
    self._tiles.append(tile)

  # this only exists to help program the tests
  # We'll need a way for the user to specify which tile they're playing
  # NOTE: We don't pop it, the game will do that if it's a valid move
  def selectRandomTile(self):
    if len(self._tiles) > 0:
      shuffle(self._tiles)
      return self._tiles[0]
    else:
      return None

  def removeTile(self, tile):
    self._tiles.remove(tile)

  @property
  def tiles(self):
    return self._tiles

  def loadFromSavedData(self,sd):
    self._name=sd['name']
     
    pd=sd['playerdata']
    for tile in pd['tiles']:
      t=Tile.newTileFromAlpha(tile)
      self._tiles.append(t)
     
  def savePlayerData(self):
    return {'tiles': self._tiles}

class TileBagGame(Game):
  _name='TileBag'
  _minPlayers=3
  _maxPlayers=5
  _playerClass=TileBagPlayer
  _starturl='/tilebag/v1'
   
  _currPlayer=0
  board=[]
  tilebag=None;
   
  def __init__(self, id):
    super().__init__(id)

  def getBoard(self):
    return self.board

  @property
  def currPlayer(self):
    return self._currPlayer

  def getPlayerInfo(self, playerid):
    pass

  def run(self):
    if not super().run():
      print("Unable to start the game - probably not enough players")
      return False;
       
    # Initialize Game Components
    print("TileBagGame Started!")
    self.board = Board(10,8)
    self.tilebag = TileBag(10,8)

    # Determine Start Order: draw a single tile for each player
    self._currPlayer = None
    lowestTile=Tile(10,8)
    for player in self._players:
      t=self.tilebag.takeTile()
      if t <= lowestTile:
        lowestTile=t
        self._currPlayer=player
      self.board.placeTile(t)

    # Now set the game order to the above
    self._rotation = islice(cycle(self._players), self._players.index(self._currPlayer)+1, None)
   
    # give each player seven tiles to start
    print(self._players)
    for player in self._players:
      for i in range(0,7):
        player.receiveTile(self.tilebag.takeTile())

  def playTile(self, playerId, tile):
    if self._started:
      if self._currPlayer.getId() == playerId:
        if tile in self._currPlayer.tiles:
          self.board.placeTile(tile)
          # TODO: ensure the above succeeds and is a valid move
          self._currPlayer.removeTile(tile)
          if self.tilebag.isEmpty():
            print("Tilebag exhausted, trigger end-game state")
          else:
            self._currPlayer.receiveTile(self.tilebag.takeTile())
          self._currPlayer=next(self._rotation)
        else:
          print("{} is not in {}".format(tile, self._currPlayer.tiles))
      else:
        print("{} is not the current player".format(playerId))
    else:
      print("game isn't started, cannot make a move")

  # Load (recreate) a version of this game from the JSON object
  def loadFromSavedData(self,sd):
    gd=sd['gamedata']
     
    # create the players
    for player in sd['players']:
      p=self.newPlayer(player['id'])
      p.loadFromSavedData(player)
      self.addPlayer(p)
      if player['id'] == gd['currPlayer']:
        self._currPlayer=p

    # restore the game state
    self._started=sd['started']
    self._rotation = islice(cycle(self._players), self._players.index(self._currPlayer)+1, None)
     
    # restore the board and the tilebag
    self.board=Board.loadFromSavedData(gd['board'])
    rows, cols =self.board.getBoardSize()
    self.tilebag=TileBag(rows, cols, initialTiles=gd['bag'])
   
  # Saves the game to json format (using the JSONEncoder from elsewhere)
  def saveGameData(self):
    return { 
      'currPlayer': self._currPlayer.getId(),
      'board': self.board.serialize(),
      'bag': self.tilebag.serialize(),
    }

SAVEDGAME="game.json"
if __name__ == "__main__":
  import os
  import json
  import base

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

      # simulate a bunch of turns
      for i in range(0,40):
        tile=tbg.currPlayer.selectRandomTile()
        if tile is None:
          print("Player ran out of tiles, ending loop")
          break
        else:
          tbg.playTile(tbg.currPlayer.getId(), tile)
  else:
    print("no saved state")

   
   
