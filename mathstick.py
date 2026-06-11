import argparse
import json
import re
import sys


# seven segment representation
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


# return the segments used by a digit
def get_segments(digit):
    return DIGITS[int(digit)]


# calculate additions and removals
def digit_difference(source_digit, target_digit):
    source_segments = get_segments(source_digit)
    target_segments = get_segments(target_digit)

    additions = target_segments - source_segments
    removals = source_segments - target_segments

    return additions, removals


# build all possible digit transitions
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


# find all possible transformations of a digit
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


# build a state from the parsed equation
def build_state(left, operator, right, result):
    return {
        "left": left,
        "operator": operator,
        "right": right,
        "result": result
    }


# convert state back to equation string
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


# check if an equation is mathematically correct
def is_valid_equation(state):
    left = int(state["left"])
    right = int(state["right"])
    result = int(state["result"])

    if state["operator"] == "+":
        return left + right == result

    return left - right == result


# create digit slots from left to right
def build_slots(state):
    slots = []

    for digit in state["left"]:
        slots.append(digit)

    for digit in state["right"]:
        slots.append(digit)

    for digit in state["result"]:
        slots.append(digit)

    return slots


def main():
    args = get_args()

    left, operator, right, result = parse_problem(args.problem)

    transitions = build_transitions()

    state = build_state(
        left,
        operator,
        right,
        result
    )

    slots = build_slots(state)

    print(state_to_string(state))
    print("Slots:", slots)
    print("Valid:", is_valid_equation(state))

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