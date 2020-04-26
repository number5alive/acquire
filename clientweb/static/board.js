var rowNames="ABCDEFGHIJKLMNOPQRSTUVWXYZ";
var defaultBoard={'ncols':12, 'nrows':9, 'occupied': ["1A", "2B", "3C"]};

function drawBoard(acquireBoard, boardinfo=defaultBoard){
  var x=boardinfo['nrows']
  var y=boardinfo['ncols']

  // flush an existing rendering of the board if it exists
  acquireBoard.innerHTML='';
   
  // Create the board grid
  for (var r=0; r<x; r++){
    var row = acquireBoard.appendChild(document.createElement("div"));
    for (var c=0; c<y; c++){
        var cellname=(c+1) + rowNames.charAt(r);         
         
        var cell=document.createElement("span");
        cell.id=cellname;
        cell.className='acquireCell';
         
        // Optional - let the user click around and set tiles
        cell.onclick = function() {boardClick(this.id);};
         
        // Add the column/row text as individual elements so we can resize
        var ctext=document.createElement("ctext");
        ctext.textContent = cellname.slice(0,-1) // column NUMBER
        cell.appendChild(ctext)
        var rtext=document.createElement("rtext");
        rtext.textContent = cellname.slice(-1) // row LETTER
        cell.appendChild(rtext)

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
      cell.className+=" highlighted";
    }
  }
}

var lastclicked=null;
function getLastClicked() {
  return lastclicked;
}

function boardClick(cellname) {
  var cell=document.getElementById(cellname);
  if( cell != null)
  {
    // only let them select an occupied cell
    if( cell.className.includes(" occupied") )
    {
      // unselect the last clicked
      if( lastclicked != null )
      {
        console.log("clearing previous click");
        lastclicked.className=lastclicked.className.replace(" selected", "");
      }
      // make the new one the last clicked
      console.log(cellname + " is the new lastclicked");
      cell.className=cell.className + " selected";
      lastclicked=cell;
    }
  }
}

function placeTile(cellname) {
  var cell=document.getElementById(cellname);
  if( cell != null)
  {
  /*
    cell.style.backgroundColor="grey";
    cell.style.color="white";
    cell.style.backgroundImage="url('static/tile.png')"
  */
    cell.className=cell.className.replace(" highlighted", "");
    cell.className+=" occupied";
  }
}
