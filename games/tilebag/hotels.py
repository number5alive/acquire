
class Stock:
  def __init__(self, name):
    self._name=name
     
  @property
  def name(self):
    return self._name

  def __repr__(self):
    return "S"+self._name
     
class Hotel:
  # chart should be an array of dicts with {'size':<formula>, 'price':<price, 'majority':<maj bonus>, 'minority':<min bonus>}
  def __init__(self, name, chart=None):
    self._name=name
    self._tile=None
    self._occupies=[]
    self._stocks=[Stock(name)]*25
    self._chart=chart

  @property
  def name(self):
    return self._name

  @property
  def size(self):
    return len(self._occupies) if self._tile else 0
     
  @property
  def tile(self):
    return self._tile

  @property
  def occupies(self):
    return self._occupies

  def setPosition(self, alpha, occupies=None):
    self._tile=alpha
    self._occupies=occupies

  def setOccupies(self, occupies):
    self._occupies=occupies

  @property
  def nstocks(self):
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

  def searchChart(self):
    if self._tile is not None and self._occupies is not None:
      currsize=len(self._occupies)
      for i in self._chart:
        if (lambda x: eval(i['size']))(currsize) == True:
          return i
    return None

  def price(self):
    curr=self.searchChart()
    if curr is not None:
      return curr['price']
    return None

  def bonuses(self):
    curr=self.searchChart()
    if curr is not None:
      return curr['maj'], curr['min']
    return None

  @staticmethod
  def loadFromSavedData(sd):
    ct=sd['charttype']
    chart=LOWEND_CHART if ct == 'low' else MIDEND_CHART if ct == 'mid' else HIGHEND_CHART
    h=Hotel(sd['name'], chart)
    h.setPosition(sd['tile'], sd['occupies'])
    h._stocks=[Stock(sd['name'])]*int(sd['stocks'])
    return h

  def serialize(self, forsave=False):
    curr=self.searchChart()
    ret = { 'name' : self._name,
            'tile' : self._tile,
            'occupies' : self._occupies,
            'stocks' : self.nstocks,
          }
    if forsave:
      minprice=self._chart[0]['price']
      charttype='low' if minprice == 200 else 'mid' if minprice == 300 else 'high'
      return { **ret,
              'charttype' : charttype,
             }
    else:
      return { **ret,
                'price' : curr['price'] if curr else None,
                'majority' : curr['maj'] if curr else None,
                'minority' : curr['min'] if curr else None,
             }
       
    return ret

LOWEND_CHART=[
     {'size':'x==2', 'price':200, 'maj':2000, 'min':1000},  
     {'size':'x==3', 'price':300, 'maj':3000, 'min':1500},  
     {'size':'x==4', 'price':400, 'maj':4000, 'min':2000},  
     {'size':'x==5', 'price':500, 'maj':5000, 'min':2500},  
     {'size':'x>=6 and x<=10', 'price':600, 'maj':6000, 'min':3000},  
     {'size':'x>=11 and x<=20', 'price':700, 'maj':7000, 'min':3500},  
     {'size':'x>=21 and x<=30', 'price':800, 'maj':8000, 'min':4000},  
     {'size':'x>=31 and x<=40', 'price':900, 'maj':9000, 'min':4500},  
     {'size':'x>=41', 'price':1000, 'maj':10000, 'min':5000},  
]
MIDEND_CHART=[
     {'size':'x==2', 'price':300, 'maj':3000, 'min':1500},  
     {'size':'x==3', 'price':400, 'maj':4000, 'min':2000},  
     {'size':'x==4', 'price':500, 'maj':5000, 'min':2500},  
     {'size':'x==5', 'price':600, 'maj':6000, 'min':3000},  
     {'size':'x>=6 and x<=10', 'price':700, 'maj':7000, 'min':3500},  
     {'size':'x>=11 and x<=20', 'price':800, 'maj':8000, 'min':4000},  
     {'size':'x>=21 and x<=30', 'price':900, 'maj':9000, 'min':4500},  
     {'size':'x>=31 and x<=40', 'price':1000, 'maj':10000, 'min':5000},  
     {'size':'x>=41', 'price':1100, 'maj':11000, 'min':5500},  
]
HIGHEND_CHART=[
     {'size':'x==2', 'price':400, 'maj':4000, 'min':2000},  
     {'size':'x==3', 'price':500, 'maj':5000, 'min':2500},  
     {'size':'x==4', 'price':600, 'maj':6000, 'min':3000},  
     {'size':'x==5', 'price':700, 'maj':7000, 'min':3500},  
     {'size':'x>=6 and x<=10', 'price':800, 'maj':8000, 'min':4000},  
     {'size':'x>=11 and x<=20', 'price':900, 'maj':9000, 'min':4500},  
     {'size':'x>=21 and x<=30', 'price':1000, 'maj':10000, 'min':5000},  
     {'size':'x>=31 and x<=40', 'price':1100, 'maj':11000, 'min':5500},  
     {'size':'x>=41', 'price':1200, 'maj':12000, 'min':6000},  
]

HOTELS=[
  {'name':"Worldwide", 'chart':LOWEND_CHART},
  {'name':"Saxxon", 'chart':LOWEND_CHART},
  {'name':"Festival", 'chart':MIDEND_CHART},
  {'name':"Imperial", 'chart':MIDEND_CHART},
  {'name':"American", 'chart':MIDEND_CHART},
  {'name':"Continental", 'chart':HIGHEND_CHART},
  {'name':"Tower", 'chart':HIGHEND_CHART},
  ]
     
if __name__ == "__main__":
  shchart=[{'size':'x==1', 'price':100, 'maj':1000, 'min':500},
           {'size':'x==2', 'price':200, 'maj':2000, 'min':1000},  
           {'size':'x>2 and x<=5', 'price':300, 'maj':3000, 'min':1500},  
           {'size':'x>5 and x<=10', 'price':400, 'maj':4000, 'min':2000},  
           {'size':'x>10', 'price':500, 'maj':5000, 'min':2500},  
          ]
  h=Hotel("SteveHotel", chart=shchart)
  print("serialized: {}".format(h.serialize()))
  h=Hotel("SteveHotel", chart=LOWEND_CHART)
  print("serialized: {}".format(h.serialize()))

  print("---- Testing Stock interactions with Hotel ----")
  print("Total Stocks in {}: {}".format(h.name, h.nstocks))
  s=h.takeStock()
  print("Total Stocks in {}: {}".format(h.name, h.nstocks))
  h.returnStock(s)
  print("Total Stocks in {}: {}".format(h.name, h.nstocks))
  [h.takeStock() for i in range(0,24)]
  print("Total Stocks in {}: {}".format(h.name, h.nstocks))
  print("takeStock: {}".format(h.takeStock()))
  print("takeStock: {}".format(h.takeStock()))
  h.returnStock(s)
  h.returnStock(s)
  h.returnStock(s)

  print("---- Testing Hotel occupation ----")
  h.setPosition("A1")
  h.setPosition("B2", ['B2', 'B3', 'C3'])
  h.setPosition("B2", occupies=['B2', 'B3', 'C3'])
  h.setOccupies(['D2', 'D3', 'E3'])

  print("---- Testing Hotel Chart Lookups ----")
  print("Hotel size {} = ${}".format(h.size, h.price()))
  h.setPosition("B2", ['B2'])
  print("Hotel size {} = ${}".format(h.size, h.price()))
  h.setPosition("B2", ['B2', 'B3'])
  print("Hotel size {} = ${}".format(h.size, h.price()))
  h.setPosition("B2", ['B2', 'B3', 'B4'])
  print("Hotel size {} = ${}".format(h.size, h.price()))
  h.setPosition("B2", ['B2', 'B3', 'B4', 'B5'])
  print("Hotel size {} = ${}".format(h.size, h.price()))
  h.setPosition("B2", ['B2', 'B3', 'B4', 'B5', 'B6'])
  print("Hotel size {} = ${}".format(h.size, h.price()))
  h.setPosition("B2", ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'])
  print("Hotel size {} = ${}".format(h.size, h.price()))
  h.setPosition("B2", ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8'])
  print("Hotel size {} = ${}".format(h.size, h.price()))
   
  print("---- Testing Hotel Serialization (save, restore) ----")
  orig=h.serialize(forsave=True)
  fs=Hotel.loadFromSavedData(orig)
  restored=fs.serialize(forsave=True)
  print("ORIG: serialized: {}".format(orig))
  print("RESTORED: serialized: {}".format(restored))
  print("{}".format("MATCH" if orig==restored else "FAIL"))
   
  print("---- Testing Restored Hotel Functionality ----")
  s=fs.takeStock()
  fs.returnStock(s)
  fs.setPosition("B2", ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'])
  print("Hotel size {} = ${}".format(fs.size, fs.price()))
    
