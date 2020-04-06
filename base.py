
 
class Game:
  def __init__(self, id, name="None"):
    # initialize the game: board, tiles, players, stocks
    self.id = id
    self.name = name
    self.started = False
    self.players = []
     
  def getId(self):
    return self.id
     
  def isStarted(self):
    return self.started

  def getPlayers(self):
    return len(self.players), self.players

  def addPlayer(self, player):
    if self.started:
      return False
    else:
      self.players.append(player)
      return True
   
  def __repr__(self):
    return 'Game ' + str(self.id) + ' (' + self.name + ')'
     
  def serialize(self):
    return {
        'id': self.id,
        'name' : self.name,
        'players' : len(self.players),
        'started' : self.started,
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
