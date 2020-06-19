
/*
Wrappers for all the calls in the lobby
Generally returns the status code, or on fail, throws an Error
*/

async function lobbyREST_getGameInfo(url) {
  const response = await fetch(url);
   
  await response.status;
  if( response.status != 200 ) {
    return Promise.reject(response.status);
  }
   
  return response.json();
}
  
async function lobbyREST_createGame(url, gameid) {
  const response = await fetch(url, {
              method: 'POST', 
                headers: {
                  Accept: 'application/json',
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                              'gametype' : 'TileBag',
                              'gameid' : gameid, })
                },
              );
                 
    await response.status;
    if( response.status == 200 || response.status == 201) {
      return true;
    } else {
      console.log("Failed to create a new game");
    }
    return false;
}
 
async function lobbyREST_addPlayer(url, playerName) {
  const response = await fetch(url, {
              method: 'POST', 
                headers: {
                  Accept: 'application/json',
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'name': playerName})
                },
              );
               
  return _responseOrError(response);
}

async function lobbyREST_startGame(url) {
  const response = await fetch(url, {
              method: 'PATCH', 
                headers: {
                  Accept: 'application/json',
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'action': 'start'})
                },
              );
               
  return _responseOrError(response);
}
  
async function _responseOrError(response) {
  await response.status;
  if( response.status == 200 || response.status == 201 ) {
    return response;
  } else {
    var errmsg="Server Error";
    await response.json()
      .then( (json) => { errmsg=json.message; });
    throw new Error(errmsg);
  }
}
