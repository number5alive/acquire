from flask import request

# Helper function - for now pull from request.arg, later from the auth token
def getCallingPlayerId():
  #TODO: check to see if a playerID token is embedded in this request (cookie)
  #      use that to provide all the private player details 
  return request.args.get('playerid')
