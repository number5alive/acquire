
 
class Game:
  def __init__(self, id, name="None"):
    # initialize the game: board, tiles, players, stocks
    self._id = id
    self._name = name
    self._started = False
    self._players = []
     
  @property
  def id(self):
    return self._id
     
  @property
  def name(self):
    return self._name

  @property
  def started(self):
    return self._started

  @property
  def players(self):
    return len(self._players), self._players

  def addPlayer(self, player):
    if self._started:
      return False
    else:
      self._players.append(player)
      return True
   
  def __repr__(self):
    return 'Game ' + str(self._id) + ' (' + self._name + ')'
     
  def serialize(self):
    return {
        'id': self._id,
        'name' : self._name,
        'players' : len(self._players),
        'started' : self._started,
     }
 
class Player:
  def __init__(self, id, name=None):
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
 
 
if __name__ == "__main__":
  game = Game(55, 'Snakes & Ladders')
  player = Player(123)

  print(game)
  print(str(game.serialize()))
  print(player)
  print(str(player.serialize()))
