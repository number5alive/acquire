from flask import Flask
from flask import jsonify
from flask import request
from Game import Game

app = Flask(__name__)
BASEURI="/acquire/v1"

games=[Game(id) for id in range(0,2)]
print(games)

"""
API
GET / Confirm Server is running
GET /games List of existing games on the server
POST /games Create a new game
"""
 
@app.route(BASEURI + '/', methods=['GET'])
def hello_world():
    return jsonify({'message' : 'Hello, World!'})
     
@app.route(BASEURI + '/games', methods=['GET'])
def get_games():
    return jsonify({'games' : [game.getId() for game in games]})
     
@app.route('/games', methods=['POST'])
def add_game():
    games.append(new_quark)
    return jsonify({'games' : games})
     
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

