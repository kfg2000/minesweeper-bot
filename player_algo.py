import random
from enum import IntEnum

from game import Game, GameState
from helper import (
    get_constrained_unopened_slots,
    get_number_of_surrounding_flags,
    get_number_of_surrounding_unopened_slots,
    get_perimeter_groups,
    get_surrounding_slots,
    get_unopened_slots,
    is_slot_unconstrained,
    risk_score_heuristic,
    run_CSP_on,
    run_EPP_on,
    run_global_CSP_on,
)


class MoveType(IntEnum):
    simple = 0
    advanced = 1
    random = 2


class PlayerAlgo:
    use_global_csp: bool = True
    last_move_played = None

    @staticmethod
    def __make_simple_logical_move(game: Game) -> bool:
        for col in range(len(game.grid)):
            for row in range(len(game.grid[0])):
                current_slot = game.grid[col][row]
                if not current_slot.is_opened:
                    continue

                number_of_surrounding_flags = get_number_of_surrounding_flags(
                    grid=game.grid, row=row, col=col
                )

                number_of_surrounding_unopened_slots = (
                    get_number_of_surrounding_unopened_slots(
                        grid=game.grid, row=row, col=col
                    )
                )

                if number_of_surrounding_flags == number_of_surrounding_unopened_slots:
                    continue

                surrounding_slots = get_surrounding_slots(
                    grid=game.grid, row=row, col=col
                )

                only_mines_unopened = (
                    current_slot.number_of_mines_around
                    == number_of_surrounding_unopened_slots
                )
                if only_mines_unopened:
                    for slot in surrounding_slots:
                        if not slot.is_opened and not slot.is_flagged:
                            slot.is_flagged = True
                    PlayerAlgo.last_move_played = MoveType.simple
                    return True

                all_mines_flagged = (
                    current_slot.number_of_mines_around == number_of_surrounding_flags
                )
                if all_mines_flagged:
                    for slot in surrounding_slots:
                        if not slot.is_opened and not slot.is_flagged:
                            game.open_slot(row=slot.row, col=slot.col)
                    PlayerAlgo.last_move_played = MoveType.simple
                    return True
        return False

    @staticmethod
    def __make_advanced_logical_move(game: Game) -> bool:
        constrained_slots = get_constrained_unopened_slots(grid=game.grid)
        if len(constrained_slots) < 3:
            return False
        end = False
        best_moves = {}
        if PlayerAlgo.use_global_csp:
            probabilities = run_global_CSP_on(
                grid=game.grid,
                constrained_slots=constrained_slots,
                remaining_mines=game.number_of_mines - game.get_flag_total(),
            )
            if not probabilities:
                return False

            for slot, probability in probabilities.items():
                if probability < 1e-6:
                    game.open_slot(row=slot.row, col=slot.col)
                    end = True
                elif probability > 1 - 1e-6:
                    slot.is_flagged = True
                    end = True
        else:
            groups = get_perimeter_groups(
                grid=game.grid, perimeter_slots=constrained_slots
            )
            use_CSP = True if game.rows <= 9 and game.cols <= 9 else groups > 10
            for group in groups:
                probabilities = (
                    run_CSP_on(grid=game.grid, grouped_slots=group)
                    if use_CSP
                    else run_EPP_on(grid=game.grid, grouped_slots=group)
                )
                if not probabilities:
                    continue

                for slot, probability in probabilities.items():
                    if probability == 0:
                        game.open_slot(row=slot.row, col=slot.col)
                        end = True
                    elif probability == 1:
                        slot.is_flagged = True
                        end = True
                    elif slot not in best_moves or probability < best_moves[slot]:
                        best_moves[slot] = probability

        if end:
            PlayerAlgo.last_move_played = MoveType.advanced
            return True
        if not best_moves or len(best_moves) == 1 and len(groups) != 1:
            return False

        lowest_prob = min(best_moves.values())
        safest_slots = [
            slot for slot, prob in best_moves.items() if abs(prob - lowest_prob) < 1e-6
        ]
        chosen_slot = random.choice(safest_slots)
        game.open_slot(row=chosen_slot.row, col=chosen_slot.col)
        PlayerAlgo.last_move_played = MoveType.advanced
        return True

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
        while game.state in [GameState.IN_PROGRESS, GameState.UNSTARTED] and (
            PlayerAlgo.__make_simple_logical_move(game)
            or PlayerAlgo.__make_advanced_logical_move(game)
        ):
            pass
        PlayerAlgo.__make_random_move(game=game)
