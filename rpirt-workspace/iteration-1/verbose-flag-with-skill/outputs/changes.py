import argparse
import sys

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="My CLI tool")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print debug information to stderr",
    )
    # ... other arguments ...
    return parser


def debug(msg: str, verbose: bool) -> None:
    """Write a debug message to stderr when verbose mode is active."""
    if verbose:
        print(f"[DEBUG] {msg}", file=sys.stderr)


def main() -> None:
    args = build_parser().parse_args()

    debug("Starting up", args.verbose)
    debug(f"Parsed args: {args}", args.verbose)

    # ... rest of program logic ...


if __name__ == "__main__":
    main()
