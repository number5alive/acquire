#!/bin/bash

PLAYERS="Colleen Geoff Higgs FSSnB"
echo "Creating a TileBag game with 4 players"
if [ $# -eq 1 ]; then
  SROOT="$1"
  ID=0
   
  # Make the game
  GURL=`curl -i -H "Content-Type: application/json" -X POST -d '{"gamename" : "TileBag"}' $SROOT/gamelobby/v1/games | tail -n 1`
  GID=`echo $GURL | sed -n 's_.*/\(.*\)$_\1_p'`
  # Add the players
  for p in $PLAYERS; do
    curl -i -H "Content-Type: application/json" -X POST -d '{"gameid":'$GID',"name":"'$p'"}' $GURL/players
  done
     
  curl -i -H "Content-Type: application/json" -X PATCH -d '{"started":"true"}' $GURL
else
  echo "Invalid args: ./$0 <serverURL>"
fi
 
