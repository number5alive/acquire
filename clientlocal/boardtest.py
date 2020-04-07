import pygame
from games.acquire.tiles import Tile
from games.acquire.board import *

SCREEN_X=500
SCREEN_Y=500
GRID_WIDTH=50
GRID_BORDER=5
BOARD_MARGIN=5
 
def drawBoardSquare(screen, board, row, col, w):
  colour=100
  if board.checkTile(row, col):
    colour=200
  x=BOARD_MARGIN + row*w
  y=BOARD_MARGIN + col*w
  pygame.draw.rect(screen, colour, (x,y,w,w))
  pygame.draw.rect(screen, 255, (x,y,w,w), GRID_BORDER)

  # Label the tile
  # TODO: center this and pick a better font ;)
  font = pygame.font.SysFont("comicsans", 20)
  text = font.render(str(Tile(row,col)), 1, (255,255,255))
  screen.blit(text, (x+w/2,y+w/2))

def redrawBoard(screen, board):
  screen.fill((128, 128, 128))
  font = pygame.font.SysFont("comicsans", 60)
  text = font.render("Click to Quit!", 1, (255,0,0))
  screen.blit(text, (100,200))
   
  # Get board size in Rows, Columns 
  rows,cols=board.getBoardSize()
  for row in range(0, rows):
    for col in range(0, cols):
      drawBoardSquare(screen, board, row, col, GRID_WIDTH)
   
  pygame.display.update()
   
def checkMouseClick(board,x,y):
  # Exit out if click was off the game window or lower half
  if x > SCREEN_X or y > SCREEN_Y/2:
    return False

  # Find out if the click was on the board or not
  try:
    t=Tile(int(x/GRID_WIDTH),int(y/GRID_WIDTH))
    board.placeTile(t)
  except Exception as e:
    pass #Click wasn't on the board
  return True

def boardLoop(screen, board):
  run = True
  clock = pygame.time.Clock()

  while run:
    clock.tick(60)
   
    redrawBoard(screen,board)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        run = False
      if event.type == pygame.MOUSEBUTTONDOWN:
        x,y=pygame.mouse.get_pos()
        if not checkMouseClick(board,x,y):
          run=False

if __name__ == "__main__":
  pygame.font.init()
  screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
  pygame.display.set_caption("Client")

  board = Board(8,5)
  # quick test   
  t=Tile(2,2)
  board.placeTile(t)
  boardLoop(screen, board)

