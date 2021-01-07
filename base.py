from json import JSONEncoder
 
def _default(self, obj, forsave=False):
  return getattr(obj.__class__, "serialize", _default.default)(obj, forsave=False)

_default.default = JSONEncoder().default #save default encoder
JSONEncoder.default = _default         #replace it
 

# Base class for a player in a game (non game-specific) 
class Player:
  def __init__(self, id, name=None):
    self.id=id
    if name is not None:
      self._name=name
    else:
      self._name="NoName"+str(id)

  def __del__(self):
    print("Deleting Player(base)")
 
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
    return self._name

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
  _currplayer=None
   
  def __init__(self, id, name="None"):
    # initialize the game: board, tiles, players, stocks
    self._id = id
    self._started = False
    self._players = []

  def __del__(self):
    print("Deleting Game(base)")
    for player in self._players:
      self._players.remove(player)
      del player

  # Child classes can override this to reset game state to original
  def reset(self):
    self._started = False
     
  @property
  def id(self):
    return self._id

  @property
  def currplayer(self):
    return self._currplayer
     
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
    return {}

  def getPublicInformation(self):
    return {}

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
 
