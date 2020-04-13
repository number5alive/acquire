var x=12;
var y=9;

colNames="ABCEDFGHIJKLMNOPQRSTUVWXYZ";

var chessBoard = document.getElementById("chessBoard");

for (var i=0; i<y; i++){
    var row = chessBoard.appendChild(document.createElement("div"));
    for (var j=0; j<x; j++){
    		cellspan=document.createElement("span");
        cellspan.textContent = (j+1) + colNames.charAt(i);
        if( j==2 && i==2 )
        {
        		blargspan=document.createElement("blarg");
            cellspan.appendChild(blargspan);
        
            //cellspan.style.backgroundColor="black";
            //cellspan.style.color="white";
        }
        row.appendChild(cellspan);
    }
}
