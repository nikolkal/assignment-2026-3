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


def main():
    args = get_args()

    left, operator, right, result = parse_problem(args.problem)

    # small test for digit transition
    additions, removals = digit_difference(1, 4)

    print("1 -> 4")
    print("add:", additions)
    print("remove:", removals)

    output = {
        "problem": args.problem,
        "max_k": args.max_k,
        "counts": {str(k): 0 for k in range(1, args.max_k + 1)},
        "nodes_visited": 0,
        "nodes_pruned": 0,
        "solutions": {str(k): [] for k in range(1, args.max_k + 1)}
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()