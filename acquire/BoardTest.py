import pygame
from Tiles import Tile
from Board import *
 
GRID_WIDTH=50
GRID_BORDER=5
 
def drawTile(screen, board, row, col, w):
  colour=100
  if board.checkTile(row, col):
    colour=200
  x=row*w
  y=col*w
  pygame.draw.rect(screen, colour, (x,y,w,w))
  pygame.draw.rect(screen, 255, (x,y,w,w), GRID_BORDER)

def redrawBoard(screen, board):
  screen.fill((128, 128, 128))
  font = pygame.font.SysFont("comicsans", 60)
  text = font.render("Click to Quit!", 1, (255,0,0))
  screen.blit(text, (100,200))
   
  # Get board size in Rows, Columns 
  rows,cols=board.getBoardSize()
  for row in range(0, rows):
    for col in range(0, cols):
      drawTile(screen, board, row, col, GRID_WIDTH)
   
  pygame.display.update()
   
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
                run = False


if __name__ == "__main__":
  pygame.font.init()
  width = 500
  height = 500
  screen = pygame.display.set_mode((width, height))
  pygame.display.set_caption("Client")

  board = Board(8,5)
  # quick test   
  t=Tile(2,2)
  board.placeTile(t)
  boardLoop(screen, board)

