"""Command-line interface for the Fly-in drone simulation."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from input.formatter_algorithm_integrado import main as run_simulation


class FlyInCLI:
    """Parse command-line options and report simulation failures cleanly."""

    def __init__(self, arguments: Sequence[str] | None = None) -> None:
        """Accept optional arguments to support testing without sys.argv."""
        self.arguments = arguments

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        """Define the mandatory map argument and optional visualization."""
        parser = argparse.ArgumentParser(
            description="Simulate drone movements through a Fly-in map."
        )
        parser.add_argument("map_file", help="Path to a Fly-in map")
        parser.add_argument(
            "--visualize",
            action="store_true",
            help="Export the Plotly turn playback as HTML",
        )
        return parser

    def run(self) -> int:
        """Execute once and return a conventional process exit status."""
        args = self.build_parser().parse_args(self.arguments)
        try:
            run_simulation(args.map_file, visualize=args.visualize)
        except KeyboardInterrupt:
            print("Interrupted by user (Ctrl+C).", file=sys.stderr)
            return 130
        except (OSError, ValueError, RuntimeError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        return 0


def main() -> int:
    """Retain the public CLI entry point."""
    return FlyInCLI().run()


if __name__ == "__main__":
    sys.exit(main())
