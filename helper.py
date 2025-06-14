from collections.abc import Sequence
from random import randint
from typing import Tuple

from models import Grid, Slot


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


def get_number_of_surrounding_flags(grid: Grid, row: int, col: int) -> int:
    positions = get_surrounding_positions(grid=grid, row=row, col=col)
    return sum(1 for pos in positions if grid[pos[1]][pos[0]].is_flagged)


def get_number_of_surrounding_unopened_slots(grid: Grid, row: int, col: int) -> int:
    positions = get_surrounding_positions(grid=grid, row=row, col=col)
    return sum(1 for pos in positions if not grid[pos[1]][pos[0]].is_opened)


def get_surrounding_slots(grid: Grid, row: int, col: int) -> Sequence[Slot]:
    positions = get_surrounding_positions(grid=grid, row=row, col=col)
    return [grid[pos[1]][pos[0]] for pos in positions]


def get_unopened_slots(grid: Grid) -> Sequence[Slot]:
    return [
        grid[col][row]
        for col in range(0, len(grid))
        for row in range(0, len(grid[0]))
        if not grid[col][row].is_opened and not grid[col][row].is_flagged
    ]


def is_slot_unconstrained(grid: Grid, row: int, col: int):
    neighbors = get_surrounding_slots(grid, row, col)
    return all(not n.is_opened for n in neighbors)


def risk_score_heuristic(grid: Grid, slot: Slot) -> Tuple[int, int]:
    surrounding = get_surrounding_slots(grid, slot.row, slot.col)

    number_of_constraints = sum(1 for n in surrounding if n.is_opened)
    number_adjacent = sum(
        1 for s in surrounding if s.is_opened and s.number_of_mines_around > 0
    )
    unopened_adjacent = sum(1 for s in surrounding if not s.is_opened)

    total_neighbors = len(surrounding)
    risk_density = (number_adjacent + unopened_adjacent) / total_neighbors
    # less contraints is better than lower risk
    return (number_of_constraints, int(risk_density * 100))
