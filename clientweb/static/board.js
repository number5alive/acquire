var x=12;
var y=9;
var colNames="ABCEDFGHIJKLMNOPQRSTUVWXYZ";

drawBoard();

function drawBoard(){
  var chessBoard = document.getElementById("chessBoard");
  for (var i=0; i<y; i++){
    var row = chessBoard.appendChild(document.createElement("div"));
    for (var j=0; j<x; j++){
        var cellname=(j+1) + colNames.charAt(i);         
         
        var cell=document.createElement("span");
        cell.setAttribute('id', cellname);
        cell.textContent = cellname;
         
        // Optional - let the user click around and set tiles
        // cell.onclick = function() {placeTile(this.id);};

        row.appendChild(cell);
    }
  }
} // drawBoard

function placeTile(cellname)
{
  console.log("placeTile: " + cellname);
  var cell=document.getElementById(cellname);
  if( cell != null)
  {
    cell.style.backgroundColor="black";
    cell.style.color="white";
    cell.style.backgroundImage="url('static/tile.png')"
  }
}
