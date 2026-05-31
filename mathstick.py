import argparse
import json
import re
import sys


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


def main():
    args = get_args()

    left, operator, right, result = parse_problem(args.problem)

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