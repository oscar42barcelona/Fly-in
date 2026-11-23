"""Command-line entry point for Fly-in."""

import argparse
import sys

from input.formatter_algorithm_integrado import main as run_simulation


def main() -> int:
    """Run a drone simulation from a map file."""
    parser = argparse.ArgumentParser(
        description="Simulate drone movements through a Fly-in map."
    )
    parser.add_argument("map_file", help="Path to a Fly-in map")
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Open the optional Pygame simulation viewer",
    )
    parser.add_argument(
        "--capacity-info",
        action="store_true",
        help="Show node and connection capacity usage after each turn",
    )
    args = parser.parse_args()

    try:
        run_simulation(
            args.map_file,
            visualize=args.visualize,
            capacity_info=args.capacity_info,
        )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
