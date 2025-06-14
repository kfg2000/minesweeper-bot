from enum import IntEnum

from helper import generate_mines, get_surrounding_mines, get_surrounding_positions
from models import Grid, Slot

NUMBER_OF_MINES = 10
ROWS: int = 9
COLS: int = 9


class GameState(IntEnum):
    UNSTARTED = 0
    IN_PROGRESS = 1
    LOST = 2
    WON = 3


class Game:
    grid: Grid
    state: GameState = GameState.UNSTARTED
    number_of_mines: int
    rows: int
    cols: int

    def __init__(
        self, number_of_mines: int = NUMBER_OF_MINES, rows: int = ROWS, cols: int = COLS
    ):
        self.number_of_mines = number_of_mines
        self.rows = rows
        self.cols = cols

        grid: list[list[Slot]] = []
        mines = generate_mines(number_of_mines, rows, cols)
        for col in range(0, cols):
            rows_list = []
            for row in range(0, rows):
                rows_list.append(Slot(row=row, col=col, has_mine=(row, col) in mines))
            grid.append(rows_list)

        for col in range(0, cols):
            for row in range(0, rows):
                slot = grid[col][row]
                if not slot.has_mine:
                    slot.number_of_mines_around = get_surrounding_mines(
                        grid=grid, row=row, col=col
                    )

        self.grid = grid

    def get_flag_total(self):
        total = 0
        for col in range(0, self.cols):
            for row in range(0, self.rows):
                total += 1 if self.grid[col][row].is_flagged else 0
        return total

    def flag_slot(self, row: int, col: int):
        slot = self.grid[col][row]
        slot.is_flagged = not slot.is_flagged

    def open_slot(self, row: int, col: int):
        if self.state == GameState.UNSTARTED:
            self.state = GameState.IN_PROGRESS
        elif self.state != GameState.IN_PROGRESS:
            return
        slot = self.grid[col][row]
        if slot.is_flagged or slot.is_opened:
            return

        slot.is_opened = True
        if slot.has_mine:
            self.lose_game()
            return
        elif slot.number_of_mines_around == 0:
            positions = get_surrounding_positions(grid=self.grid, row=row, col=col)
            for pos in positions:
                self.open_slot(pos[0], pos[1])

        self.check_win()

    def check_win(self):
        remaining = 0
        for row in self.grid:
            for slot in row:
                remaining += 0 if slot.is_opened else 1

        if remaining <= NUMBER_OF_MINES:
            self.win_game()

    def win_game(self):
        for col in range(0, COLS):
            for row in range(0, ROWS):
                if not self.grid[col][row].is_opened:
                    self.grid[col][row].is_flagged = True
        self.state = GameState.WON

    def lose_game(self):
        for col in range(0, COLS):
            for row in range(0, ROWS):
                self.grid[col][row].is_opened = True
                self.grid[col][row].is_flagged = False
        self.state = GameState.LOST
