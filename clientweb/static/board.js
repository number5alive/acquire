var colNames="ABCDEFGHIJKLMNOPQRSTUVWXYZ";

function drawBoard(acquireBoard, boardinfo){
  var x=boardinfo['ncols']
  var y=boardinfo['nrows']

  // flush an existing rendering of the board if it exists
  acquireBoard.innerHTML='';
   
  // Create the board grid
  for (var j=0; j<x; j++){
    var row = acquireBoard.appendChild(document.createElement("div"));
    for (var i=0; i<y; i++){
        var cellname=(j+1) + colNames.charAt(i);         
         
        var cell=document.createElement("span");
        cell.setAttribute('id', cellname);
        cell.textContent = cellname;
         
        // Optional - let the user click around and set tiles
        // cell.onclick = function() {placeTile(this.id);};

        row.appendChild(cell);
    }
  }
   
  // place any tiles that are already occupied
  for(var i=0; i<boardinfo['occupied'].length; i++)
  {
    placeTile(boardinfo['occupied'][i])
  }

} // drawBoard

function showOptions(tiles) {
  for(var i=0; i<tiles.length; i++){
    var cell=document.getElementById(tiles[i]);
    if( cell != null)
    {
      cell.style.backgroundColor="#FFFFCC";
    }
  }
}

function placeTile(cellname) {
  var cell=document.getElementById(cellname);
  if( cell != null)
  {
    cell.style.backgroundColor="black";
    cell.style.color="white";
    cell.style.backgroundImage="url('static/tile.png')"
  }
}
