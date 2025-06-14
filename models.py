from collections.abc import Sequence


class Slot:
    has_mine: bool
    row: int
    col: int
    is_flagged: bool = False
    is_opened: bool = False
    number_of_mines_around: int = 0

    def __init__(self, row, col, has_mine):
        self.row = row
        self.col = col
        self.has_mine = has_mine

    def __str__(self):
        return f"slot_{self.row}_{self.col}"

    def __eq__(self, other):
        if not isinstance(other, Slot):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))


Grid = Sequence[Sequence[Slot]]
