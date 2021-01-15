/*
Wrappers for all the fetch calls in the tilebag rest API
Generally returns the status code, or on fail, throws an Error with the
message from the game
*/
 
 
async function tbREST_ailist(url) {
  const response = await fetch(url);

  await response.status;
  if( response.status == 200 ) {
    return response.json()
  } else {
    var errmsg="Server Error";
    await response.json()
      .then( (json) => { errmsg=json.message; });
    throw new Error(errmsg);
  }
}
 
async function tbREST_aiadd(url) {
  const response = await fetch(url, {
              method: 'POST', 
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
              },
              },
            );
               
  return _responseOrError(response);
}
 
async function tbREST_airemove(url, tile) {
  const response = await fetch(url, {
              method: 'DELETE', 
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
              },
              },
            );
               
  return _responseOrError(response);
}
 
 
async function tbREST_placetile(url, tile) {
  const response = await fetch(url, {
              method: 'PATCH', 
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 'action':'placetile', 
                                      'tile':tile})
              },
            );
               
  return _responseOrError(response);
}

async function tbREST_placeHotel(url, hotel, position){
  // make REST call to change player hotel amounts by this
  const response = await fetch(url, {
              method: 'PATCH', 
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 'action':'placeHotel', 
                                    'hotel' : hotel,
                                    'tile' : position,
                                  })
              },
            );

  return _responseOrError(response);
}

async function tbREST_stockAction(url, hotel, amount) {
  // make REST call to change player hotel amounts by this
  const response = await fetch(url, {
              method: 'PATCH', 
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 'action':'buystocks', 
                                    'hotel' : hotel,
                                    'amount' : amount,
                                  })
              },
            );
             
  return _responseOrError(response);
}
 
async function tbREST_requestEndGame(url) {
  // make REST call to change player hotel amounts by this
  const response = await fetch(url, {
              method: 'PATCH', 
              headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ 'endgame':'yeahletsdoit', 
                                  })
              },
            );
             
  return _responseOrError(response);
}

async function tbREST_getGameState(url) {
  const response = await fetch(url);

  await response.status;
  if( response.status == 200 ) {
    return response.json()
  } else {
    var errmsg="Server Error";
    await response.json()
      .then( (json) => { errmsg=json.message; });
    throw new Error(errmsg);
  }
}

async function _responseOrError(response) {
  await response.status;
  if( response.status == 200 ) {
    return response;
  } else {
    var errmsg="Server Error";
    await response.json()
      .then( (json) => { errmsg=json.message; });
    throw new Error(errmsg);
  }
}
