import pygame
from Tiles import Tile
from Board import *
 
def redrawBoard(screen, board):
  screen.fill((128, 128, 128))
  font = pygame.font.SysFont("comicsans", 60)
  text = font.render("Click to Quit!", 1, (255,0,0))
  screen.blit(text, (100,200))
   
  x=0
  y=0
  w=50
  col_tile=100
  col_free=200
   
  # Get board size in Rows, Columns 
  rows,cols=board.getBoardSize()
  for row in range(0, rows):
    for col in range(0, cols):
      if board.checkTile(row, col):
        pygame.draw.rect(screen, col_tile, (x,y,w,w))
      else:
        pygame.draw.rect(screen, col_free, (x,y,w,w))
      x+=w
    x=0      
    y+=w
   
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

