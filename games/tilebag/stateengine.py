
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

    def on_event(self, event, **kwargs):
        """
        Handle events that are delegated to this State.
        """
        pass # should return ret, nextState

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

    def toHuman(self):
      return "Waiting for player to {}".format(str(self))
 
class StateEngine():
  def __init__(self, start):
    self._currplayer=None
    #self._players=None
    self._start=start
    self._state=start # our current state

  @property
  def currplayer(self):
    return self._currplayer
     
  def on_event(self, player, event, **kwargs):
    """
    This is the bread and butter of the state machine. Incoming events are
    delegated to the given states which then handle the event. The result is
    then assigned as the new state.
    """

    # Let the first state have no player, otherwise enforce current player
    # presumption is that the first state WILL set the _currplayer value
    # TODO: make sure this all works as intended, as written:
    #       will not support concurrent actions (like stock transactions)
    ret=False
    if self._start == self._state or self._currplayer == player:
      # The current state can keep or modify the state on return
      ret, self._state = self._state.on_event(event, **kwargs)
    else:
      print("Not the current player, cannot take action")
    return ret

  def serialize(self, forsave=False):
    return { 'currplayer' : self._currplayer,
             'state' : str(self._state),
             'stateinfo' : self._state.serialize(forsave),
             'message' : self._state.toHuman(), }

if __name__ == "__main__":
  # Test the state machine Engine with a few states
  class TestGame(StateEngine):
    def __init__(self):
      print("TestGameEngine")
      self._blah="hello!";
      super().__init__(TestGame.StateA(self))
       
    class StateA(State):
      def on_event(self, event, **kwargs):
        print("StateA")
        if event == 'hi':
          self._game._currplayer = 'timmy'
          print("Hit 'hi' event from 'StateB', testing _currplayer access {}".format(self._game._currplayer))
          return True, TestGame.StateB(self._game)
        else:
          print("invalidA")
        return False, self

    class StateB(State):
      def on_event(self, event, **kwargs):
        print("StateB")
        if event == 'bye':
          print("Hit event 'bye' from 'StateB', testing Game access {}".format(self._game._blah))
          return True, TestGame.StateA(self._game)
        else:
          print("invalidB")
        return False, self

      def toHuman(self):
        return "Waiting for something something StateB something"

  print("---- Testing basic state transition mechanics ----")
  engine=TestGame()
  engine.on_event('timmy', 'hi')
  engine.on_event('timmy', 'hi')
  engine.on_event('billy', 'bye')
  engine.on_event('timmy', 'bye')
  engine.on_event('timmy', 'hi')
  engine.on_event('timmy', 'bye')

  print("---- Testing Serialization ----")
  print(engine.serialize(False))
  engine.on_event('timmy', 'hi')
  print(engine.serialize(False))

