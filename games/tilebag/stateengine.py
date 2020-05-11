
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

    # override if you pass other variables to init
    # loadFromSaveData will pass these as-is as kwargs (I think)
    def serialize(self, forsave=False):
      return {}

    def toHuman(self):
      return "Waiting for player to {}".format(str(self))

class StateEventLog():
  def __init__(self, start, end, player, event, kwargs):
    self._start=start
    self._end=end
    self._player=player
    self._event=event
    self._kwargs=kwargs

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return "STATECHANGE: {} -> {} on {} from {} with args: {}".format(str(start), str(end), event, player.name, kwargs)
  
 
class StateEngine():
  def __init__(self, start, fOnStateTx):
    self._currplayer=None
    #self._players=None
    self._start=start
    self._state=start # our current state
    self._end=None
    self._fOnStateTx=fOnStateTx
    self._eventlog=[]

  @property
  def currplayer(self):
    return self._currplayer

  def triggerEnd(self, endState):
    self._end=endState
     
  def on_event(self, player, event, **kwargs):
    """
    This is the bread and butter of the state machine. Incoming events are
    delegated to the given states which then handle the event. The result is
    then assigned as the new state.
    """

    # Let the first state have no player, otherwise enforce current player
    # presumption is that the first state WILL set the _currplayer value
    ret=False
    if self._start == self._state or self._currplayer == player:
      ret, newState = self._state.on_event(event, **kwargs)

      # on successful operations, make a state-tx check, and record the event
      if ret:
        self._fOnStateTx()
        self._eventlog.append(StateEventLog(self._start, newState, player, event, kwargs))
        self._state=newState
      return ret, newState
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

