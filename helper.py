from collections.abc import Sequence
from random import randint
from typing import Tuple

from models import Grid


def generate_mines(
    number_of_mines: int, rows: int, columns: int
) -> Sequence[Tuple[int, int]]:
    mines = set()
    # TODO: make more efficient
    while len(mines) < number_of_mines:
        x = randint(0, rows - 1)
        y = randint(0, columns - 1)
        mines.add((x, y))
    return mines


def get_surrounding_positions(
    grid: Grid, row: int, col: int
) -> Sequence[Tuple[int, int]]:
    positions = []
    max_col = len(grid) - 1
    max_row = len(grid[0]) - 1

    for dt_y in range(-1, 2):
        for dt_x in range(-1, 2):
            x = row + dt_x
            y = col + dt_y
            if (
                (dt_x == 0 and dt_y == 0)
                or (x < 0 or y < 0)
                or (x > max_row or y > max_col)
            ):
                continue

            positions.append((x, y))
    return positions


def get_surrounding_mines(grid: Grid, row: int, col: int) -> int:
    positions = get_surrounding_positions(grid=grid, row=row, col=col)
    return sum(1 for pos in positions if grid[pos[1]][pos[0]].has_mine)
