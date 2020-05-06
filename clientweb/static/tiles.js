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
    makeTileDragable(tile, dropzone);
  }
}
 
function makeTileDragable(elmnt, dropz, onDragAction=null){
  var origx = 0, origy = 0;
  var origbg = "";
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  var crossingDropZone = false;
  var origZindex=elmnt.style.zIndex;    

  elmnt.onmousedown = dragMouseDown;
    
  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    origx = elmnt.offsetLeft;
    origy = elmnt.offsetTop;
    origbg = elmnt.style.backgroundColor;
    elmnt.style.zIndex=10;  // make sure dragged item is always on top
    elmnt.dataset.hasmoved=false; // might just be a click
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
    if( onDragAction )
    {
      onDragAction(elmnt, false);
    }
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;

    // set the flag to indicate that this object moved
    // TODO: check for a minimum amount of moving?
    elmnt.dataset.hasmoved = true;
     
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    
    watchDropZones();
  }
  
  function watchDropZones()
  {
    var overlaps = false;
    for( var i=0; i<dropz.length && !overlaps; i++)
    {
      overlaps = overlapsDropZone(elmnt, dropz[i][0]);
    }

    // Change how it displays if it's crossing into an area
    if( overlaps && !elmnt.className.includes(" overlaps") )
    {
      elmnt.className = elmnt.className + " overlaps";
    }
    else if( !overlaps && elmnt.className.includes(" overlaps") )
    {
      elmnt.className=elmnt.className.replace(" overlaps", "");
    }
  }
   
  // returns true if tile element overlaps dz element
  function overlapsDropZone(tile, dz) {
    var rect1=tile.getBoundingClientRect();
    var rect2=dz.getBoundingClientRect();
    return !(rect1.right < rect2.left || 
             rect1.left > rect2.right || 
             rect1.bottom < rect2.top || 
             rect1.top > rect2.bottom)
  }

  function closeDragElement() {
    /* stop moving when mouse button is released:*/
    document.onmouseup = null;
    document.onmousemove = null;
    if( onDragAction )
    {
      onDragAction(elmnt, true);
    }

    for( var i=0; i<dropz.length; i++)
    {
      if( overlapsDropZone(elmnt, dropz[i][0]) )
      {
        dropz[i][0].dispatchEvent(new CustomEvent(dropz[i][1], {bubbles: true, detail: { text: () => textarea.value, tile: elmnt }}));
        break;
      }
    }

    // snap-back to the original position
    elmnt.style.top = (origy) + "px";
    elmnt.style.left = (origx) + "px";
    elmnt.style.backgroundColor = origbg;
    elmnt.className=elmnt.className.replace(" overlaps", "");
    elmnt.style.zIndex=origZindex;   
  }
} 
