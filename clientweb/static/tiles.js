/* WARNING: very little of this code is salvageable! toss it out and start again! */
/* Got lazy and using addEffect code from tilebag.html, so this isn't even self-contained anymore! */

const NUMTILES=7;

// This function is called from the main game engine, to render the tiles in the tilerack
function setTiles(rackname, tiles, dropzone=null, order=false){
  // Get a handle to the rack that holds the tiles - we'll need this to twiddle with how they look
  var rackspots = document.getElementsByClassName(rackname);
   
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
      tile = createTile(tiles[i], dropzone, rackspots);
      newtiles.push(tile);
      newTile=true; // why both? you'll see!
    }
    alltiles.push(tile);
  }
  
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

function createTile(tilename, dropzone, rackspots){
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
    makeTileDragable(tile, dropzone, rackspots);
  }

  return tile;
}

// Handles tile movement and actions (now includes click-to-play and drag-and-drop) 
function makeTileDragable(elmnt, dropz, rackspots){
  var origx = 0, origy = 0;
  var origbg = "";
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  var crossingDropZone = false;
  var origZindex=elmnt.style.zIndex;    

  elmnt.dataset.clickCount=0;
  elmnt.onmousedown = onMouseDown;
    
  function onMouseDown(e) {
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
    document.onmouseup = onDragDone;
    // call a function whenever the cursor moves:
    document.onmousemove = onDragElement;
     
    // Keep track of which tile was last selected
    updateTileSelection();
  }
   
  function updateTileSelection() {
    // loop through the rackspots, clear what was selected and select this one
    for( var i = 0; i < rackspots.length; i++) {
      // make sure there's a tile in the current slot
      if( rackspots[i].childNodes.length != 0 ) {
        var rackTile=rackspots[i].childNodes[0];
        // if it's not the current tile, clear any other selected tile, make this one selected
        if( rackTile == elmnt ) {
          addEffect(EFFECT_HIGHLIGHT, rackTile);
        } else {
          removeEffect(EFFECT_HIGHLIGHT, rackTile);
          rackTile.dataset.clickCount=0;
        }
      }
    }
  }

  function onDragElement(e) {
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

  function onDragDone() {
    /* stop moving when mouse button is released:*/
    document.onmouseup = null;
    document.onmousemove = null;

    if( elmnt.dataset.hasmoved == 'true')
    {
      // See if the object being moved overlaps with a dropzone, and if so fire an event
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
    } else {
      // it was just a click, we can use this!
      var clickCount=parseInt(elmnt.dataset.clickCount) + 1;
      console.log("It was just a click! " + clickCount);
       
      // trigger a game action if they've clicked a set number of times
      if( clickCount >= 3 )
      {
        // KLUDGE! We're only calling this with ONE dropzone (the gameboard), so this is "safe"
        //         older code had multiple dropzones, but we're not doing that anymore
        //         if we change anything with drop zones, this will fail miserably!
        //         have fun troubleshooting this little gem :/ sorry future steve
        dropz[0][0].dispatchEvent(new CustomEvent(dropz[0][1], {bubbles: true, detail: { text: () => textarea.value, tile: elmnt }}));
      }
       
      // update the click count
      elmnt.dataset.clickCount=clickCount;
    }
  }
} 
