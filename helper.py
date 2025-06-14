from collections import defaultdict, deque
from collections.abc import Mapping, Sequence, Set
from random import randint
from typing import Dict, Tuple

from constraint import Problem

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


def get_opened_constraint_slots_near_group(grid: Grid, group: Set[Slot]) -> Set[Slot]:
    slots = set()
    for col in range(len(grid)):
        for row in range(len(grid[0])):
            slot = grid[col][row]
            if (
                slot.is_opened
                and slot.number_of_mines_around > 0
                and (
                    set(get_surrounding_slots(grid=grid, row=slot.row, col=slot.col))
                    & group
                )
            ):
                slots.add(slot)
    return slots


def is_slot_unconstrained(grid: Grid, row: int, col: int):
    neighbors = get_surrounding_slots(grid, row, col)
    return all(not n.is_opened for n in neighbors)


def get_constrained_unopened_slots(grid: Grid) -> Sequence[Slot]:
    return [
        grid[col][row]
        for col in range(0, len(grid))
        for row in range(0, len(grid[0]))
        if not grid[col][row].is_opened
        and not grid[col][row].is_flagged
        and any(
            slot.is_opened
            for slot in get_surrounding_slots(grid=grid, row=row, col=col)
        )
    ]


def check_config(grid: Grid, flagged_slots: Set[Slot]) -> bool:
    for slot in flagged_slots:
        surrounding_slots = get_surrounding_slots(grid=grid, row=slot.row, col=slot.col)
        for ss in surrounding_slots:
            if (
                ss.is_opened
                and ss.number_of_mines_around
                < get_number_of_surrounding_flags(grid=grid, row=ss.row, col=ss.col)
            ):
                return False

    return True


def flag_slots(slots: Set[Slot]) -> None:
    for slot in slots:
        slot.is_flagged = True


def unflag_slots(slots: Set[Slot]) -> None:
    for slot in slots:
        slot.is_flagged = False


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


def get_perimeter_groups(
    grid: Grid, perimeter_slots: Sequence[Slot]
) -> Sequence[Sequence[Slot]]:
    slot_neighbors = defaultdict(set)
    for col in range(len(grid)):
        for row in range(len(grid[0])):
            slot = grid[col][row]
            if slot.is_opened and slot.number_of_mines_around > 0:
                neighboring_slots = get_surrounding_slots(grid=grid, row=row, col=col)
                for neighbor in neighboring_slots:
                    if neighbor in perimeter_slots:
                        slot_neighbors[(row, col)].add(neighbor)

    adjacency = defaultdict(set)
    for neighbors in slot_neighbors.values():
        neighbors_list = list(neighbors)
        for i in range(len(neighbors_list)):
            for j in range(i + 1, len(neighbors_list)):
                adjacency[neighbors_list[i]].add(neighbors_list[j])
                adjacency[neighbors_list[j]].add(neighbors_list[i])

    visited = set()
    groups = []
    for slot in perimeter_slots:
        if slot in visited:
            continue

        group = []
        queue = deque([slot])
        visited.add(slot)
        while queue:
            current = queue.popleft()
            group.append(current)
            for adjacent_slot in adjacency[current]:
                if adjacent_slot not in visited:
                    queue.append(adjacent_slot)
                    visited.add(adjacent_slot)
        groups.append(group)
    return groups


def run_EPP_on(grid: Grid, grouped_slots: Sequence[Slot]) -> Mapping[int, float]:
    bits_length = len(grouped_slots)
    max_configs = 2**bits_length
    successful_configs = []
    for bits in range(max_configs):
        config_combinations = [i for i in range(bits_length) if (bits >> i) & 1]
        to_flag = {grouped_slots[i] for i in config_combinations}
        flag_slots(slots=to_flag)
        if check_config(grid=grid, flagged_slots=to_flag):
            successful_configs.append(config_combinations)
        unflag_slots(slots=to_flag)

    probabilities = {}
    for i in range(0, bits_length):
        probabilities[grouped_slots[i]] = sum(
            1.0 for config in successful_configs if i in config
        ) / len(successful_configs)
    return probabilities


def run_CSP_on(grid: Grid, grouped_slots: Sequence[Slot]) -> Mapping[Slot, float]:
    problem = Problem()
    variable_map = {}  # map position to var name
    reverse_map = {}  # map var name to slot
    for slot in grouped_slots:
        var_name = str(slot)
        variable_map[(slot.row, slot.col)] = var_name
        reverse_map[var_name] = slot
        problem.addVariable(var_name, [0, 1])

    for opened_slot in get_opened_constraint_slots_near_group(
        grid=grid, group=set(grouped_slots)
    ):
        unflagged_vars = []
        flagged_count = 0
        neighbors = get_surrounding_slots(
            grid=grid, row=opened_slot.row, col=opened_slot.col
        )
        for neighbor in neighbors:
            if neighbor.is_flagged:
                flagged_count += 1
            elif not neighbor.is_opened:
                key = (neighbor.row, neighbor.col)
                if key in variable_map:
                    unflagged_vars.append(variable_map[key])
        if not unflagged_vars:
            continue

        total_mines = opened_slot.number_of_mines_around - flagged_count
        problem.addConstraint(
            lambda *vals, total=total_mines: sum(vals) == total, unflagged_vars
        )

    solutions = problem.getSolutions()
    probabilities = {}
    if not solutions:
        return probabilities

    for var_name, slot in reverse_map.items():
        probabilities[slot] = sum(1 for s in solutions if s[var_name] == 1) / len(
            solutions
        )

    return probabilities


def run_global_CSP_on(
    grid: Grid, constrained_slots: Sequence[Slot], remaining_mines: int
) -> Mapping[Slot, float]:
    problem = Problem()
    variable_map = {}  # map position to var name
    reverse_map = {}  # map var name to index (in constrained_slots)
    for slot in constrained_slots:
        var_name = str(slot)
        variable_map[(slot.row, slot.col)] = var_name
        reverse_map[var_name] = slot
        problem.addVariable(var_name, [0, 1])

    for opened_slot in get_opened_constraint_slots_near_group(
        grid=grid, group=set(constrained_slots)
    ):
        unflagged_vars = []
        flagged_count = 0
        neighbors = get_surrounding_slots(
            grid=grid, row=opened_slot.row, col=opened_slot.col
        )
        for neighbor in neighbors:
            if neighbor.is_flagged:
                flagged_count += 1
            elif not neighbor.is_opened:
                key = (neighbor.row, neighbor.col)
                if key in variable_map:
                    unflagged_vars.append(variable_map[key])
        if not unflagged_vars:
            continue

        total_mines = opened_slot.number_of_mines_around - flagged_count
        problem.addConstraint(
            lambda *vals, total=total_mines: sum(vals) == total, unflagged_vars
        )

    problem.addConstraint(
        lambda *vals: sum(vals) <= remaining_mines,
        [variable_map[(s.row, s.col)] for s in constrained_slots],
    )

    solutions = problem.getSolutions()
    if not solutions or len(solutions) < 10:
        return {}

    probabilities: Dict[Slot, float] = {slot: 0 for slot in constrained_slots}

    for sol in solutions:
        for var_name, val in sol.items():
            if val == 1:
                probabilities[reverse_map[var_name]] += 1

    # Normalize
    for slot in probabilities:
        probabilities[slot] /= len(solutions)

    return probabilities
