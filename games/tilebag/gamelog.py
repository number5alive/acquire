
 
class GameAction():
  def __init__(self, who, what, details=None):
    self._who = who
    self._what = what
    self._details = details

  def serialize(self, forsave=False):
    ret={ 'action': self._what }
    if self._who is not None:
      ret['player'] = self._who
    if self._details is not None:
      ret['details'] = self._details
    return ret

  def toString(self):
    if self._what == 'message':
      return self._details['message']
    elif self._what == 'playTile':
      return "{} played tile {}".format(self._who, self._details)
    elif self._what == 'stockAction':
      action='bought'
      amt=self._details['amount']
      if amt < 0:
        action='sold'
        amt = -amt
      hotel=self._details['hotel']
      return "{} {} {} stocks in {}".format(self._who, action, amt, hotel)
    elif self._what == 'moneyAction':
      action='received'
      amt=self._details
      if amt < 0:
        action='spent'
        amt=-amt
      return "{} {} ${}".format(self._who, action, amt)
    elif self._what == 'removeHotel':
      return "{} has been removed from the board".format(self._details)
    elif self._what == 'placeHotel':
      hotel=self._details['hotel']
      location=self._details['location']
      return "{} has been placed on the board at {}".format(hotel, location)
    else:
      return str(self)

  def __repr__(self):
    return str(self.serialize())
  
class GameLog():
  def __init__(self):
    self._actions = []

  def append(self, action):
    self._actions.append(action)
    print("GAMELOG: {}".format(action))

  def recordAction(self, who, what, details):
    action=GameAction(who, what, details)
    self.append(action)

  def recordGameMessage(self, message, details=None):
    extDetails={"message": message}
    if details is not None:
      extDetails['details'] = details
    action=GameAction(None, 'message', extDetails)
    self.append(action)

  def recordMoneyAction(self, player, amount):
    action=GameAction(player, 'moneyAction', amount)
    self.append(action)

  def recordStockAction(self, player, hotel, amount):
    extDetails={"hotel": hotel, "amount": amount}
    action=GameAction(player, 'stockAction', extDetails)
    self.append(action)

  def recordRemoveHotelAction(self, hotel):
    action=GameAction(None, 'removeHotel', hotel)
    self.append(action)

  def recordPlaceHotelAction(self, hotel, location):
    extDetails={"hotel": hotel, "location": location}
    action=GameAction(None, 'placeHotel', extDetails)
    self.append(action)

  def recordTileAction(self, player, tilealpha):
    action=GameAction(player, 'playTile', tilealpha)
    self.append(action)
    pass

  def serialize(self, forsave=False, last=0):
    actionlist=self._actions[::-1]
    if last > 0:
      actionlist=actionlist[:last]

    return [act.toString() for act in actionlist]
     
if __name__ == "__main__":
  print("---- Testing GameAction Class ----")
  a1=GameAction('billy', 'playTile', '4B')
  a2=GameAction('sally', 'buyStock', '{ "hotel" : "American", "amount": 3}')
  
  print(a1.serialize())
  print(a2.serialize())
  print(a2)
   
  print("---- Testing GameLog Class ----")
  log=GameLog()
  log.append(a1)
  log.append(a2)
  log.recordGameMessage('somethingKewl', 'a bunch of stuff')
  log.recordMoneyAction('timmy', -27000)
  log.recordStockAction('frank', 'Global', 7)
  log.recordPlaceHotelAction('Canadian', '7B')
  log.recordRemoveHotelAction('Spire')
  log.recordTileAction('jimmy', '5B')
  print("Entire Log: {}".format(log.serialize()))
  print("Last Entry: {}".format(log.serialize(last=1)))
  print("Last 3 Entries: {}".format(log.serialize(last=3)))

   
