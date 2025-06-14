from enum import IntEnum

from game import Game, GameState
from helper import (
    get_unopened_slots,
    is_slot_unconstrained,
    risk_score_heuristic,
)


class MoveType(IntEnum):
    simple = 0
    advanced = 1
    random = 2


class PlayerAlgo:
    last_move_played = None

    @staticmethod
    def __make_random_move(game: Game) -> None:
        if game.state == GameState.UNSTARTED:
            middle_row = game.rows // 2
            middle_col = game.cols // 2
            game.open_slot(row=middle_row, col=middle_col)
            PlayerAlgo.last_move_played = MoveType.random
            return
        unopened_slots = get_unopened_slots(grid=game.grid)
        if not unopened_slots:
            return

        # check edges and corners
        for slot in unopened_slots:
            if slot.row in {0, game.rows - 1} or slot.col in {
                0,
                game.cols - 1,
            }:
                if is_slot_unconstrained(grid=game.grid, row=slot.row, col=slot.col):
                    game.open_slot(row=slot.row, col=slot.col)
                    PlayerAlgo.last_move_played = MoveType.random
                    return

        # check interior slots
        for slot in unopened_slots:
            if slot.row in {0, game.rows - 1} or slot.col in {0, game.cols - 1}:
                continue
            if is_slot_unconstrained(grid=game.grid, row=slot.row, col=slot.col):
                game.open_slot(row=slot.row, col=slot.col)
                PlayerAlgo.last_move_played = MoveType.random
                return

        # get least constrained slot
        fallback = min(
            unopened_slots,
            key=lambda slot: risk_score_heuristic(grid=game.grid, slot=slot),
        )
        game.open_slot(row=fallback.row, col=fallback.col)
        PlayerAlgo.last_move_played = MoveType.random

    @staticmethod
    def make_a_move(game: Game) -> None:
        PlayerAlgo.__make_random_move(game=game)
