import argparse
import json
import re


# seven segment representation
# segment 0 is the middle horizontal segment
# segments 1-6 go clockwise starting from the top
DIGITS = {
    0: {1, 2, 3, 4, 5, 6},
    1: {2, 3},
    2: {0, 1, 2, 4, 5},
    3: {0, 1, 2, 3, 4},
    4: {0, 2, 3, 6},
    5: {0, 1, 3, 4, 6},
    6: {0, 1, 3, 4, 5, 6},
    7: {1, 2, 3, 6},
    8: {0, 1, 2, 3, 4, 5, 6},
    9: {0, 1, 2, 3, 4, 6}
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", required=True)
    parser.add_argument("--max-k", type=int, default=2)
    return parser.parse_args()


def parse_problem(problem):
    pattern = r"^\s*(\d+)\s*([+\-])\s*(\d+)\s*=\s*(\d+)\s*$"
    match = re.match(pattern, problem)

    if not match:
        raise ValueError("Invalid problem format")

    left = match.group(1)
    operator = match.group(2)
    right = match.group(3)
    result = match.group(4)

    return left, operator, right, result


def get_segments(digit):
    return DIGITS[int(digit)]


def digit_difference(source_digit, target_digit):
    source_segments = get_segments(source_digit)
    target_segments = get_segments(target_digit)

    additions = target_segments - source_segments
    removals = source_segments - target_segments

    return additions, removals


def build_transitions():
    transitions = {}

    for source in range(10):
        transitions[source] = {}

        for target in range(10):
            additions, removals = digit_difference(source, target)

            transitions[source][target] = {
                "add": len(additions),
                "remove": len(removals),
                "delta": len(additions) - len(removals)
            }

    return transitions


def get_digit_moves(digit, transitions):
    moves = []

    for target in range(10):
        info = transitions[digit][target]

        moves.append({
            "target": target,
            "add": info["add"],
            "remove": info["remove"],
            "delta": info["delta"]
        })

    return moves


def build_state(left, operator, right, result):
    return {
        "left": left,
        "operator": operator,
        "right": right,
        "result": result
    }


def state_to_string(state):
    return (
        state["left"]
        + " "
        + state["operator"]
        + " "
        + state["right"]
        + " = "
        + state["result"]
    )


def is_valid_equation(state):
    left = int(state["left"])
    right = int(state["right"])
    result = int(state["result"])

    if state["operator"] == "+":
        return left + right == result

    return left - right == result


def build_slots(state):
    slots = []

    for digit in state["left"]:
        slots.append(digit)

    for digit in state["right"]:
        slots.append(digit)

    for digit in state["result"]:
        slots.append(digit)

    return slots


def generate_slot_moves(state, transitions):
    slots = build_slots(state)
    all_moves = []

    for index, digit in enumerate(slots):
        digit_moves = get_digit_moves(
            int(digit),
            transitions
        )

        all_moves.append({
            "position": index,
            "digit": digit,
            "moves": digit_moves
        })

    return all_moves


def apply_move(state, position, new_digit):
    left = list(state["left"])
    right = list(state["right"])
    result = list(state["result"])

    left_size = len(left)
    right_size = len(right)

    if position < left_size:
        left[position] = str(new_digit)
    elif position < left_size + right_size:
        index = position - left_size
        right[index] = str(new_digit)
    else:
        index = position - left_size - right_size
        result[index] = str(new_digit)

    return {
        "left": "".join(left),
        "operator": state["operator"],
        "right": "".join(right),
        "result": "".join(result)
    }


# operator changes: try target + and target -
def operator_cost(source_operator, target_operator):
    if source_operator == target_operator:
        return 0, 0, 0

    if source_operator == "-" and target_operator == "+":
        operator_add = 1
        operator_remove = 0
    elif source_operator == "+" and target_operator == "-":
        operator_add = 0
        operator_remove = 1
    else:
        operator_add = 0
        operator_remove = 0

    operator_delta = operator_remove - operator_add

    return operator_add, operator_remove, operator_delta


def build_operator_options(source_operator):
    options = []

    for target_operator in ["+", "-"]:
        operator_add, operator_remove, operator_delta = operator_cost(
            source_operator,
            target_operator
        )

        options.append({
            "operator": target_operator,
            "operator_add": operator_add,
            "operator_remove": operator_remove,
            "operator_delta": operator_delta
        })

    return options


def digit_delta_interval(digit, transitions, max_k):
    values = []

    for target in range(10):
        info = transitions[int(digit)][target]

        if info["add"] <= max_k and info["remove"] <= max_k:
            values.append(info["delta"])

    return min(values), max(values)


def build_suffix_intervals(slots, transitions, max_k):
    intervals = []

    for digit in slots:
        intervals.append(
            digit_delta_interval(
                digit,
                transitions,
                max_k
            )
        )

    suffix = [(0, 0)] * (len(slots) + 1)

    for i in range(len(slots) - 1, -1, -1):
        current_min, current_max = intervals[i]
        next_min, next_max = suffix[i + 1]

        suffix[i] = (
            current_min + next_min,
            current_max + next_max
        )

    return intervals, suffix


# first simple DFS skeleton
def dfs_slots(index, slots, current_digits, transitions, stats):
    stats["nodes_visited"] += 1

    if index == len(slots):
        return

    digit = int(slots[index])

    moves = get_digit_moves(
        digit,
        transitions
    )

    for move in moves:
        current_digits.append(move["target"])

        dfs_slots(
            index + 1,
            slots,
            current_digits,
            transitions,
            stats
        )

        current_digits.pop()


def main():
    args = get_args()

    left, operator, right, result = parse_problem(
        args.problem
    )

    transitions = build_transitions()

    state = build_state(
        left,
        operator,
        right,
        result
    )

    slots = build_slots(state)

    slot_moves = generate_slot_moves(
        state,
        transitions
    )

    operator_options = build_operator_options(operator)

    intervals, suffix = build_suffix_intervals(
        slots,
        transitions,
        args.max_k
    )

    print(state_to_string(state))
    print("Slots:", slots)
    print("Valid:", is_valid_equation(state))
    print("Number of slots:", len(slot_moves))
    print("Moves for first slot:")
    print(slot_moves[0])
    print("Operator options:")
    print(operator_options)
    print("Digit intervals:")
    print(intervals)
    print("Suffix intervals:")
    print(suffix)

    new_state = apply_move(
        state,
        0,
        7
    )

    print("After move:")
    print(state_to_string(new_state))

    stats = {
        "nodes_visited": 0,
        "nodes_pruned": 0
    }

    dfs_slots(
        0,
        slots,
        [],
        transitions,
        stats
    )

    print("DFS stats:", stats)

    output = {
        "problem": args.problem,
        "max_k": args.max_k,
        "counts": {
            str(k): 0
            for k in range(1, args.max_k + 1)
        },
        "nodes_visited": 0,
        "nodes_pruned": 0,
        "solutions": {
            str(k): []
            for k in range(1, args.max_k + 1)
        }
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()