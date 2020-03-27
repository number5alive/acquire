from flask import Flask
from flask import jsonify
from flask import request, abort
from Game import Game

app = Flask(__name__)
BASEURI="/acquire/v1"

games=[Game(id) for id in range(0,2)]
print(games)

"""
API
GET / Confirm Server is running
GET /games List of existing games on the server
GET /games?id= Get details about a specific game
POST /games {'id'} Start a game
"""
 
@app.route(BASEURI + '/', methods=['GET'])
def hello_world():
    return jsonify({'message' : 'Hello, World!'})
     
def getGameById(id):
  for i,q in enumerate(games):
    currId=q.getId()
    if currId == id:
      return games[i]
  return None

def getGameByReq():
  req_id=request.values.get('gameid')
  req_game=None
  if req_id is not None and req_id.isdigit():
    req_id=int(req_id) # we read it from the request as a string
    req_game=getGameById(req_id)
  return req_id, req_game
 
@app.route(BASEURI + '/games', methods=['GET'])
def get_games():
  req_id, req_game = getGameByReq()
  if req_id is not None:
    print("get one game: " + str(req_id))
    if req_game is not None:
      return jsonify({'game' : req_game.serialize()})
    else:
      abort(404) #no such game
  else:
    return jsonify({'games' : [game.getId() for game in games]})

@app.route(BASEURI + '/players', methods=['GET'])
def get_players():
  abort(404)
     
     
"""
@app.route(BASEURI + '/games', methods=['POST'])
def startGame():
  req_id, req_game = getGameByReq()
  print(req_id)
  print(req_game)
  if req_id and req_game:
    if req_game.isStarted():
      abort(500)
    else:
      req_game.start()
      return jsonify({'game' : req_game.serialize()})
  abort(404)
"""

if __name__ == "__main__":
    app.run(debug=True)
     
"""
@app.route('/quarks', methods=['GET'])
def returnAll():
    return jsonify({'quarks' : quarks})

@app.route('/quarks/<string:name>', methods=['GET'])
def returnOne(name):
    theOne = quarks[0]
    for i,q in enumerate(quarks):
      if q['name'] == name:
        theOne = quarks[i]
    return jsonify({'quarks' : theOne})

@app.route('/quarks', methods=['POST'])
def addOne():
    new_quark = request.get_json()
    quarks.append(new_quark)
    return jsonify({'quarks' : quarks})

@app.route('/quarks/<string:name>', methods=['PUT'])
def editOne(name):
    new_quark = request.get_json()
    for i,q in enumerate(quarks):
      if q['name'] == name:
        quarks[i] = new_quark    
    qs = request.get_json()
    return jsonify({'quarks' : quarks})

@app.route('/quarks/<string:name>', methods=['DELETE'])
def deleteOne(name):
    for i,q in enumerate(quarks):
      if q['name'] == name:
        del quarks[i]  
    return jsonify({'quarks' : quarks})
"""

