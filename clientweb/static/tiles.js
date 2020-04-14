const NUMTILES=7;
 
function drawTileRack(rackelem, dropzone=null){
  for(var i=0;i<NUMTILES;i++)
  {
    // Create a tile div so we can append to the list
    var tile = document.createElement('div');
    tile.className = 'tile';
    tile.id = 'tile'+i;
     
    // TODO: query the stylesheet directly to get the default width
    tile.style.left = 10+i*(80+10) + "px";

    // Save us a step later, if a drop-zone is identified then we definitely
    // want our tile to be dragable
    if(dropzone != null){
      makeTileDragable(tile, dropzone);
    }
   
    // Add the new tile to the list of tiles
    rackelem.appendChild(tile);
  }
}
 
function makeTilesDragable(rackelem, dropzone) {
  // Iterate through the objects on the rack, make all tiles movalbe
  for (var i = 0; i < rackelem.childNodes.length; i++) {
    if (rackelem.childNodes[i].className == "tile") {
      makeTileDragable(rackelem.childNodes[i], dropzone);
    }
  }
}

function makeTileDragable(elmnt, dropzone=null){
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  var crossingDropZone = false;

  elmnt.onmousedown = dragMouseDown;
   
  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    
    if( dropzone != null){
      watchDropZone();
    }
  }
  
  function watchDropZone()
  {
    var overlaps = overlapsDropZone(elmnt);
    if( !crossingDropZone )
    {
      if( overlaps )
      {
        // we weren't crossing, now are
        crossingDropZone = true;
        elmnt.style.backgroundColor = 'yellow';
      }
    }
    else
    {
      if( !overlaps )
      {
        // we WERE crossing, but now aren't
        crossingDropZone = false;
        elmnt.style.backgroundColor = 'WhiteSmoke';
      }
    }
  }
   
  function overlapsDropZone(tile) {
    var rect1=tile.getBoundingClientRect();
    var rect2=dropzone.getBoundingClientRect();
    return !(rect1.right < rect2.left || 
             rect1.left > rect2.right || 
             rect1.bottom < rect2.top || 
             rect1.top > rect2.bottom)
  }

  function closeDragElement() {
    /* stop moving when mouse button is released:*/
    document.onmouseup = null;
    document.onmousemove = null;

    if(dropzone != null && crossingDropZone ){
      console.log("hold on to your butts!");
      dropzone.dispatchEvent(new CustomEvent('playtile', {bubbles: true, detail: { text: () => textarea.value, tile: elmnt }}));
    }
  }
} 
