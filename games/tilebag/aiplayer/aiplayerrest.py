from flask import jsonify

TILEBAGAIREST_URL='/ai'
 
# Expose these routes to the main server application 
from flask import Blueprint
tilebagairest_blueprint = Blueprint('tilebagiarest_blueprint', __name__)

@tilebagairest_blueprint.route('/', methods=['GET'])
def rest_tilebagai_hello():
    ''' GET the number of AI players currently playing games '''
    return jsonify({'message' : 'Hello, AI World!'})
