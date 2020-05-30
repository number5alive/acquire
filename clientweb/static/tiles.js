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
  var tilesize=rackpos.clientWidth;
  tilesize-=25;
  tile.style.height = tilesize + 'px';
  tile.style.minWidth = tilesize + 'px';
}

function setTiles(rackspace, tiles, dropzone=null, order=false){
  // if we're getting rid of existing tiles, loop through and remove them
  if( order ){
    tiles.sort(function (a, b) {
      var aval=parseInt(a.slice(0,-1))*100 + a.charCodeAt(a.length-1);
      var bval=parseInt(b.slice(0,-1))*100 + b.charCodeAt(b.length-1);
      return aval - bval;
    });
  }

  // loop through the tiles, make sure they exist
  var alltiles=[];
  var newtiles=[];
  var newTile=false;
  for(var i=0; i<tiles.length; i++){
    // Get the tile if it exists
    var tile=document.getElementById('tile'+tiles[i]);
    if( null == tile ) {
      // Or make it if it's new
      tile = createTile(tiles[i], dropzone);
      newtiles.push(tile);
      newTile=true; // why both? you'll see!
    }
    alltiles.push(tile);
  }
  
  var rackspots = document.getElementsByClassName(rackspace);
  // loop through the rack, cleanup old, drop in new
  for( var i = 0; i < rackspots.length; i++) {
    if( rackspots[i].childNodes.length != 0 ) {
      // there's something in this space
      // See if it's a "dead" tile and remove
      // OR just remove it if we're re-ordering the rack
       
      if( !alltiles.includes(rackspots[i].childNodes[0]) || (newTile && order) ) {
        rackspots[i].removeChild(rackspots[i].childNodes[0]);
        i-=1;
        continue; // we need this because we'll fill the next free spot
      }

      // If we reach here, there's a tile and it should stay there

    } else if( newTile ) {// Only update the rack if we have new tiles
      // Nothing in this spot, drop a tile there!
      var tile=order ? alltiles.shift() : newtiles.shift(); // see?!
      if( tile != undefined ) {
        rackspots[i].appendChild(tile);
      } else {
        rackspots[i].innerHTML="";
      }
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

  // Save us a step later, if a drop-zone is identified then we definitely
  // want our tile to be dragable
  if(dropzone != null){
    makeTileDragable(tile, dropzone);
  }

  return tile;
}

// Add a single tile to the tile rack
// it's text and id will be set to the value of the tile
function addTile(rackname, tilename, dropzone=null){
   
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
}
 
function makeTileDragable(elmnt, dropz, onDragAction){
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
    if( onDragAction != undefined && onDragAction != null )
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
             rect1.top > rect2.bottom);
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
