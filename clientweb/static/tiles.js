const NUMTILES=7;
 
function makeTileRack(rackelem, dropzone=null){
  for(var i=0;i<NUMTILES;i++)
  {
    var ph=document.createElement('span');
    ph.className='tilerack';
    rackelem.appendChild(ph);
  }

  window.addEventListener("resize", function(){sizeTiles(rackelem);});
}

function sizeTiles(rackelem) {
  // Iterate through the objects on the rack, make all tiles movable
  for (var i = 0; i < rackelem.childNodes.length; i++) {
    if (rackelem.childNodes[i].childNodes.length != 0 &&
        rackelem.childNodes[i].childNodes[0].className == "tile") {
      sizeTile(rackelem.childNodes[i].childNodes[0],rackelem.childNodes[i]);
    }
  }
}

function sizeTile(tile, rackpos) {
  tilesize=rackpos.clientWidth;
  tilesize-=25;
  tile.style.height = tilesize + 'px';
  tile.style.minWidth = tilesize + 'px';
}

function setTiles(rack, tiles, dropzone=null, flush=false){
  // if we're getting rid of existing tiles, loop through and remove them
  if( flush ){
  }

  // loop through the tiles, make sure they don't exist, then add them
  for(var i=0; i<tiles.length; i++){
    // make sure the tile isn't in the list before trying to add it
    if( null == document.getElementById('tile'+tiles[i]) )
    {
      addTile(rack, tiles[i], dropzone);
    }
  }
}

function createTile(tilename, dropzone){
  // Create a tile div so we can append to the list
  var tile = document.createElement('div');
  tile.className = 'tile';
  tile.id = 'tile'+tilename;

  // Add the column/row text as individual elements so we can resize
  var ctext=document.createElement("ctext");
  ctext.textContent = tilename.slice(0,-1); // column NUMBER
  tile.appendChild(ctext);
  var rtext=document.createElement("rtext");
  rtext.textContent = tilename.slice(-1); // row LETTER
  tile.appendChild(rtext);

  return tile;
}

// Add a single tile to the tile rack
// it's text and id will be set to the value of the tile
function addTile(rackname, tilename, dropzone=null){
  var tile = createTile(tilename);
   
  // find an empty spot in the rack for which to place it
  var rackpos = null;
  var rackspots = document.getElementsByClassName(rackname);
  for (var i = 0; i < rackspots.length; i++) {
    if (rackspots[i].childNodes.length == 0) {
      rackpos = rackspots[i];
      break;
    }
  }
   
  if(rackpos != null)
  {
    rackpos.appendChild(tile);
  }

  // Save us a step later, if a drop-zone is identified then we definitely
  // want our tile to be dragable
  if(dropzone != null){
//    makeTileDragable(tile, dropzone);
  }
}
 
function makeTilesDragable(rackelem, dropzone) {
  // Iterate through the objects on the rack, make all tiles movable
  for (var i = 0; i < rackelem.childNodes.length; i++) {
    if (rackelem.childNodes[i].childNodes.length != 0 &&
        rackelem.childNodes[i].childNodes[0].className == "tile") {
      makeTileDragable(rackelem.childNodes[i].childNodes[0], dropzone);
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
      dropzone.dispatchEvent(new CustomEvent('playtile', {bubbles: true, detail: { text: () => textarea.value, tile: elmnt }}));
    }
  }
} 
