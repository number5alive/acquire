
class Stock:
  def __init__(self, name):
    self._name=name
     
  @property
  def name(self):
    return self._name

  def __repr__(self):
    return "S"+self._name
     
class Hotel:
  def __init__(self, name):
    self._name=name
    self._tile=None
    self._occupies=[]
    self._stocks=[Stock(name)]*25

  @property
  def name(self):
    return self._name
     
  @property
  def tile(self):
    return self._tile

  @property
  def occupies(self):
    return self._occupies

  def setPosition(self, alpha, occupies):
    self._tile=alpha
    self._occupies=occupies

  def setOccupies(self, occupies):
    self._occupies=occupies

  def stocksRemaining(self):
    return len(self._stocks)

  def takeStock(self):
    if len(self._stocks) > 0:
      return self._stocks.pop()
    return None

  def returnStock(self, stock):
    if stock.name == self.name:
      self._stocks.append(stock)
      return True
    else:
      return False

  def serialize(self):
    return {
      'name' : self._name,
      'tile' : self._tile,
      'occupies' : self._occupies,
      'stocks' : len(self._stocks)
    }
     
if __name__ == "__main__":
  h=Hotel("SteveHotel")

  print("---- Testing Stock interactions with Hotel ----")
  print("Total Stocks in {}: {}".format(h.name, h.stocksRemaining()))
  s=h.takeStock()
  print("Total Stocks in {}: {}".format(h.name, h.stocksRemaining()))
  h.returnStock(s)
  print("Total Stocks in {}: {}".format(h.name, h.stocksRemaining()))
  [h.takeStock() for i in range(0,24)]
  print("Total Stocks in {}: {}".format(h.name, h.stocksRemaining()))
  print("takeStock: {}".format(h.takeStock()))
  print("takeStock: {}".format(h.takeStock()))

  print("---- Testing Hotel occupation ----")
  h.setPosition("A1")
  h.setPosition("B2", ['B2', 'B3', 'C3'])
  h.setPosition("B2", occupies=['B2', 'B3', 'C3'])
  h.setOccupies(['D2', 'D3', 'E3'])
   
  print("---- Testing Hotel Serialization ----")
  print("serialized: {}".format(h.serialize()))
    
