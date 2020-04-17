
# Base class for a player in a game (non game-specific) 
class Player:
  def __init__(self, id, name=None):
    print("base.Player")
    self.id=id
    if name is not None:
      self.name=name
    else:
      self.name="NoName"+str(id)
 
  def getId(self):
    return self.id

  def getName(self):
    return self.name

  def setName(self, name):
    self.name=name

  def __repr__(self):
    return 'Player ' + self.name
     
  def serialize(self):
    return {
        'id': self.id,
        'name': self.name,
     }
 
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

  # child classes really need to override this puppy
  def run(self):
    self._started = True

  def stop(self):
    self._started = False;
   
  def __repr__(self):
    return 'Game ' + str(self._id) + ' (' + self._name + ')'

  @classmethod
  def serialize(self,cls):
    return {
        'id': cls._id,
        'name' : cls._name,
        'numplayers' : len(cls._players),
        'players' : [p.serialize() for p in cls._players],
        'started' : cls._started,
     }
      
if __name__ == "__main__":
  game = Game(55, 'Snakes & Ladders')
  player = Player(123)

  print(game)
  print(str(game.serialize()))
  print(player)
  print(str(player.serialize()))
 
