from base import Game

class TileBag(Game):
  _name='TileBag'
  _minPlayers=3
  _maxPlayers=5
   
  def __init__(self, id):
    super().__init__(id)

if __name__ == "__main__":
  print("name: " + TileBag.name())
  print("min: " + str(TileBag.minPlayers()))
  print("max: " + str(TileBag.maxPlayers()))

