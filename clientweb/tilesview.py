from flask import render_template
 
# Expose these routes to the main server application 
from flask import Blueprint
tilesview_blueprint = Blueprint('tilesview_blueprint', __name__,
                  template_folder='templates')

BASEURI="/acquire/v1" #for now, we'll move this later
 
@tilesview_blueprint.route(BASEURI + '/tiletest', methods=['GET'])
def get_tiletest():
  return render_template('showtiles.html')
 
