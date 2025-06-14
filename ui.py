from typing import Sequence

from pygame import BLEND_RGBA_MULT, SRCALPHA, Rect, Surface, font, image, transform

from game import Game, Slot

WIDTH, HEIGHT = 600, 600
OFFSET_X, OFFSET_Y = 50, 50

open_slot_images = None
closed_slot_image = None
mine_image = None
flag_image = None


def _tint_image(image, tint_color):
    """Darken image by blending with tint_color (R, G, B, A)"""
    tinted_image = image.copy()
    tint_surface = Surface(image.get_size(), SRCALPHA)
    tint_surface.fill(tint_color)
    tinted_image.blit(tint_surface, (0, 0), special_flags=BLEND_RGBA_MULT)
    return tinted_image


def load_images(column_size: int):
    slot_size = WIDTH // column_size
    global open_slot_images, closed_slot_image, mine_image, flag_image
    open_slot_images = []
    temp = image.load("assets/default.png").convert_alpha()
    open_slot_images.append(transform.scale(temp, (slot_size, slot_size)))
    for i in range(1, 9):
        temp = image.load(f"assets/{i}.png").convert_alpha()
        open_slot_images.append(transform.scale(temp, (slot_size, slot_size)))

    temp = image.load("assets/default.png").convert_alpha()
    temp = _tint_image(temp, (128, 128, 128, 255))
    closed_slot_image = transform.scale(temp, (slot_size, slot_size))

    temp = image.load("assets/mine.png").convert_alpha()
    mine_image = transform.scale(temp, (slot_size, slot_size))

    temp = image.load("assets/flag.png").convert_alpha()
    flag_image = transform.scale(temp, (slot_size, slot_size))


def get_slot_image(slot: Slot) -> Surface:
    if slot.is_flagged:
        return flag_image
    if not slot.is_opened:
        return closed_slot_image
    if slot.has_mine:
        return mine_image
    return open_slot_images[slot.number_of_mines_around]


CollisionRects = Sequence[Sequence[Rect]]


def draw_board(screen: Surface, game: Game) -> CollisionRects:
    screen.fill("white")
    grid = []
    slot_size = WIDTH // game.cols
    for col in range(game.cols):
        rows = []
        for row in range(game.rows):
            x = col * slot_size + OFFSET_X
            y = row * slot_size + OFFSET_Y
            rows.append(screen.blit(get_slot_image(game.grid[col][row]), (x, y)))
        grid.append(rows)
    return grid


def win_screen(screen: Surface):
    text_surface = font.Font(None, 36).render("CONGRATS! YOU WIN", True, "green")
    text_rect = text_surface.get_rect()
    right_padding = 20
    text_rect.topright = (screen.get_width() - right_padding, 50)
    screen.blit(text_surface, text_rect)


def lose_screen(screen: Surface):
    text_surface = font.Font(None, 36).render("GAME OVER! YOU LOSE", True, "red")
    text_rect = text_surface.get_rect()
    right_padding = 20
    text_rect.topright = (screen.get_width() - right_padding, 50)
    screen.blit(text_surface, text_rect)
