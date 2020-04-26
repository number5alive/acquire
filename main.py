from server import app, socketio
 
# This stub of a file is required for Google App Engine
# The real magic is in server.py
if __name__ == "__main__":
  app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # stops the browser from caching

  socketio.run(app, debug=True)
  #app.run(debug=True)
  print("server stopping")
