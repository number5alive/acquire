from base import Game
from base import Player

class TileBagPlayer(Player):
  def __init__(self, id, name=None):
    print("init'ing a TileBag player")
    super().__init__(id)

class TileBag(Game):
  _name='TileBag'
  _minPlayers=3
  _maxPlayers=5
  _currPlayer=0
   
  def __init__(self, id):
    print("Init'ing a TileBag game")
    super().__init__(id)
    self._playerClass=TileBagPlayer

  def run(self):
    print("Starting TileBag!!!!!")
    super().run()
    # TODO: init the game

if __name__ == "__main__":
  print("name: " + TileBag.name())
  print("min: " + str(TileBag.minPlayers()))
  print("max: " + str(TileBag.maxPlayers()))

