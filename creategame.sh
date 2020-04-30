#!/bin/bash

PLAYERS="Colleen Geoff Higgs FSSnB"
 
function createGame() {
  SROOT="$1"
  SPECGID="$2"

  # Make the game
  GURL=`curl -i -H "Content-Type: application/json" -X POST -d '{'$SPECGID'"gametype" : "TileBag"}' $SROOT/gamelobby/v1/games | tail -n 1`

  GID=`echo $GURL | sed -n 's_.*/\(.*\)$_\1_p'`
  # Add the players
  for p in $PLAYERS; do
    curl -i -H "Content-Type: application/json" -X POST -d '{"gameid":"'$GID'","name":"'$p'"}' $GURL/players
  done
     
  curl -i -H "Content-Type: application/json" -X PATCH -d '{"action":"start"}' $GURL
} 
  
echo "Creating a TileBag game with 4 players"
if [ $# -eq 1 ]; then
  SROOT="$1"
  createGame $SROOT ""
elif [ $# -eq 2 ]; then
  SROOT="$1"
  SPECGID='"gameid":"'$2'", '
  createGame $SROOT $SPECGID
else
  echo "Invalid args: ./$0 <serverURL> [gamename]"
fi

