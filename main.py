import pygame

from game import Game, GameState
from ui import draw_board, load_images, lose_screen, win_screen

# pygame setup
pygame.init()
pygame.display.set_caption("Minesweeper")
screen = pygame.display.set_mode((1280, 720))
game = Game()
collision_grid = []
running = True

holding = False
hold_start_time = 0
HOLD_THRESHOLD = 500  # ms → 500ms = 0.5 seconds → adjust as needed

load_images(game.cols)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            game = Game()

        if game.state != GameState.IN_PROGRESS:
            break

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and collision_grid
        ):
            holding = True
            hold_start_time = pygame.time.get_ticks()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and holding:
            holding = False
            hold_duration = pygame.time.get_ticks() - hold_start_time

            for col in range(0, game.cols):
                for row in range(0, game.rows):
                    if collision_grid[col][row].collidepoint(event.pos):
                        if hold_duration > HOLD_THRESHOLD:
                            game.flag_slot(row, col)
                        else:
                            game.open_slot(row, col)

    collision_grid = draw_board(screen=screen, game=game)

    if game.state == GameState.LOST:
        lose_screen(screen=screen)
    elif game.state == GameState.WON:
        win_screen(screen=screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

# limits FPS to 60
# dt is delta time in seconds since last frame, used for framerate-
# independent physics.

pygame.quit()
