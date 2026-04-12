"""
Example CLI with --verbose flag that prints debug info to stderr.
"""

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Example CLI tool")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (debug info printed to stderr)",
    )
    parser.add_argument("--input", type=str, help="Input value to process")
    return parser.parse_args()


def log_debug(message: str, verbose: bool) -> None:
    """Print debug message to stderr when verbose mode is enabled."""
    if verbose:
        print(f"[DEBUG] {message}", file=sys.stderr)


def main():
    args = parse_args()

    log_debug(f"Parsed arguments: {args}", args.verbose)
    log_debug(f"verbose={args.verbose}, input={args.input}", args.verbose)

    # Main logic
    if args.input:
        log_debug(f"Processing input: {args.input!r}", args.verbose)
        result = args.input.upper()
        log_debug(f"Result computed: {result!r}", args.verbose)
        print(result)
    else:
        log_debug("No input provided, printing usage hint", args.verbose)
        print("No input provided. Use --input <value>.")


if __name__ == "__main__":
    main()
