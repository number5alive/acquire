
# Base class for a player in a game (non game-specific) 
class Player:
  def __init__(self, id, name=None):
    print("base.Player")
    self.id=id
    if name is not None:
      self._name=name
    else:
      self._name="NoName"+str(id)
 
  def getId(self):
    return self.id

  def getName(self):
    return self._name

  @property
  def name(self):
    return self._name

  def setName(self, name):
    self._name=name

  def __repr__(self):
    return 'Player ' + self._name

  # child classes can override this to save player specific information
  def savePlayerData(self):
    return []
     
  def serialize(self, forsave=False):
    serdata = {
        'id': self.id,
        'name': self._name,
     }
    if forsave:
      serdata['playerdata']=self.savePlayerData()
    return serdata;
 
# Base class for every game on this platform
class Game:
  _minPlayers=0
  _maxPlayers=0
  _name="None"
  _starturl="/"
  _playerClass=Player
   
  def __init__(self, id, name="None"):
    # initialize the game: board, tiles, players, stocks
    self._id = id
    self._started = False
    self._players = []
     
  @property
  def id(self):
    return self._id
     
  @classmethod
  def name(cls):
    return cls._name

  @classmethod
  def fullname(cls):
    return cls.__module__ + '.' + cls.__qualname__

  @classmethod
  def starturl(cls):
    return cls._starturl

  @classmethod
  def config(cls):
    return {"name": cls.name(), "class": cls.fullname(), "starturl": cls._starturl}
     
  @classmethod
  def minPlayers(cls):
    return cls._minPlayers

  @classmethod
  def maxPlayers(cls):
    return cls._maxPlayers

  @property
  def started(self):
    return self._started

  @property
  def players(self):
    return len(self._players), self._players

  @property
  def newPlayer(self):
    return self._playerClass

  def addPlayer(self, player):
    if self._started:
      return False
    else:
      self._players.append(player)
      return True

  # child classes will implement this method to start their game, only
  # basic checks will happen in the base clase
  def run(self):
    if len(self._players) >= self._minPlayers and len(self._players) <= self._maxPlayers:
      self._started = True
    return self._started;

  def stop(self):
    self._started = False;
   
  def __repr__(self):
    return 'Game ' + str(self._id) + ' (' + self._name + ')'

  def saveGameData(self):
    return []

  def serialize(self,forsave=False):
    serdata = {
        'id': self._id,
        'name' : self._name,
        'numplayers' : len(self._players),
        'players' : [p.serialize(forsave) for p in self._players],
        'started' : self._started,
    }
    if forsave:
      serdata['gamedata']=self.saveGameData()
    return serdata
      
if __name__ == "__main__":
  game = Game(55, 'Snakes & Ladders')
  player = Player(123)

  print(game)
  print(str(game.serialize()))
  print(player)
  print(str(player.serialize()))
 
