
class State():
    """
    Base class for the states of our game
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    NOTE: States will extend this 
    """

    def __init__(self, game=None):
        print('Initializing state: {}'.format(str(self)))
        self._game=game

    def on_event(self, event):
        """
        Handle events that are delegated to this State.
        """
        print("Handling event {} from {}".format(event, str(self)))

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__

    def serialize(self, forsave=False):
      return {}
 
class StateEngine():
  def __init__(self, currplayer, start):
    self._currplayer=currplayer
    self._state=start

  @property
  def currplayer(self):
    return self._currplayer
     
  def on_event(self, player, event):
    """
    This is the bread and butter of the state machine. Incoming events are
    delegated to the given states which then handle the event. The result is
    then assigned as the new state.
    """

    # The next state will be the result of the on_event function.
    # TODO: make sure this all works as intended, as written:
    #       will not support concurrent actions (like stock transactions)
    if self._currplayer == player:
      self._state = self._state.on_event(event)
    else:
      print("Not the current player, cannot take action")

  def serialize(self, forsave=False):
    return { 'currplayer' : self._currplayer,
             'state' : str(self._state),
             'stateinfo' : self._state.serialize(forsave) }

if __name__ == "__main__":
  # Test the state machine Engine with a few states
  class TestGame(StateEngine):
    def __init__(self, player):
      self._blah="hello!";
      super().__init__(player, TestGame.StateA(game=self));
      print("TestGameEngine")
       
    class StateA(State):
      def on_event(self, event):
        print("StateA")
        if event == 'hi':
          print("Hit 'hi' event from 'StateB', testing _currplayer access {}".format(self._game._currplayer))
          return TestGame.StateB(self._game)
        else:
          print("invalidA")
        return self

    class StateB(State):
      def on_event(self, event):
        print("StateB")
        if event == 'bye':
          print("Hit event 'bye' from 'StateB', testing Game access {}".format(self._game._blah))
          return TestGame.StateA(self._game)
        else:
          print("invalidB")
        return self

  print("---- Testing basic state transition mechanics ----")
  engine=TestGame('timmy')
  engine.on_event('timmy', 'hi')
  engine.on_event('timmy', 'hi')
  engine.on_event('billy', 'bye')
  engine.on_event('timmy', 'bye')
  engine.on_event('timmy', 'hi')
  engine.on_event('timmy', 'bye')

  print("---- Testing Serialization ----")
  print(engine.serialize(False))

