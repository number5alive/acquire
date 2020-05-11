
 
class GameLog():
  def __init__(self):
    self._log = []

  def append(self, message):
    print("GAMELOG: {}".format(message))
    self._log.append(message)

  def recordGameMessage(self, message):
    self.append(message)

  def recordMerger(self, big, small):
    self.append("*** {} is buying out {} ***".format(big, small))

  def recordBonusPayout(self, player, btype, amount):
    self.append("{} received {} shareholder bonus of {}".format(player, btype.upper(), amount))

  def recordMoneyAction(self, player, amount):
    self.append("{} {} ${}".format(player, "received" if amount > 0 else "spent", amount))

  def recordStockAction(self, player, hotel, amount, totalcost=0):
    action="bought" if amount > 0 else "sold"
    txcost="" if totalcost==0 else " for a total of {}".format(totalcost)
    self.append("{} {} {} stocks in {}{}".format(player, action, amount, hotel ,txcost))
     
  def recordStockTrade(self, player, fromhotel, tohotel, rxamount):
    self.append("{} traded {} stocks of {} for {} stocks in {}".format(player, rxamount*2, fromhotel, rxamount, tohotel))

  def recordRemoveHotelAction(self, hotel):
    self.append("{} has been removed from the board".format(hotel))

  def recordPlaceHotelAction(self, hotel, location):
    self.append("{} has been placed on the board at {}".format(hotel, location))

  def recordTileAction(self, player, tilealpha):
    self.append("{} played tile {}".format(player, tilealpha))

  def serialize(self, forsave=False, last=0):
    loglist=self._log[::-1]
    if last > 0:
      loglist=loglist[:last]

    return [log for log in loglist]
     
if __name__ == "__main__":
  print("---- Testing GameLog Class ----")
  log=GameLog()
  log.recordGameMessage('somethingKewl')
  log.recordBonusPayout('timmy', 'minOritY', 2000)
  log.recordMoneyAction('timmy', -27000)
  log.recordStockAction('frank', 'Global', 7)
  log.recordStockTrade('frank', 'Global', 'Anglo', 6)
  log.recordPlaceHotelAction('Canadian', '7B')
  log.recordRemoveHotelAction('Spire')
  log.recordTileAction('jimmy', '5B')
  print("Entire Log: {}".format(log.serialize()))
  print("Last Entry: {}".format(log.serialize(last=1)))
  print("Last 3 Entries: {}".format(log.serialize(last=3)))

   
