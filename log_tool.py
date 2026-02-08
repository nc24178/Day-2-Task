"""
PL202 — Day 2 (45 min) — Log Filter CLI Tool (Individual)

You will create a command-line tool that:
- Reads logs.txt
- Ignores invalid lines
- Filters by --level and/or --service (optional)
- Writes matching valid lines to an output file (--out, default: filtered_logs.txt)
- Prints a short summary

Log format (valid line):
  timestamp | level | service | message

Valid rules:
  - exactly 4 fields after splitting by '|'
  - level (after uppercasing) is one of: INFO, WARN, ERROR

Examples:
  python log_tool.py --level ERROR
  python log_tool.py --service auth --out auth_logs.txt
  python log_tool.py --level WARN --service api --out warn_api.txt
"""

import argparse
from pathlib import Path

LOG_FILE = Path("logs.txt")
DEFAULT_OUT = "filtered_logs.txt"
ALLOWED_LEVELS = {"INFO", "WARN", "ERROR"}


def parse_line(line: str):
    """
    Parse a log line.
    Returns (timestamp, level, service, message) OR None if invalid format.

    NOTE:
    - Empty lines are invalid.
    - Split by '|', trim whitespace around each part.
    - Must have exactly 4 parts.
    """
    if not line:
        return None
    raw = line.strip()
    if not raw:
        return None
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) != 4:
        return None
    timestamp, level, service, message = parts
    return timestamp, level, service, message


def is_valid_level(level: str) -> bool:
    """Return True if level is one of INFO/WARN/ERROR."""
    return level.strip().upper() in ALLOWED_LEVELS


def matches_filters(level: str, service: str, level_filter, service_filter) -> bool:
    """Return True if the line matches the provided filters."""
    if level_filter is not None and level.upper() != level_filter:
        return False
    if service_filter is not None and service != service_filter:
        return False
    return True


def build_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argparse parser."""
    parser = argparse.ArgumentParser(description="Filter cloud logs by level and/or service.")
    parser.add_argument(
        "--level",
        type=str,
        required=False,
        help="Level to filter (INFO, WARN, ERROR). Case-insensitive.",
    )
    parser.add_argument(
        "--service",
        type=str,
        required=False,
        help="Service to filter (e.g., auth, api, db). Case-sensitive.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=DEFAULT_OUT,
        required=False,
        help="Output filename (default: filtered_logs.txt)",
    )
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    level_filter = args.level.upper() if getattr(args, "level", None) else None
    service_filter = args.service if getattr(args, "service", None) else None
    out_path = Path(args.out)

    if not LOG_FILE.exists():
        # Keep to the 3-line summary shape even if missing file
        print("Valid lines scanned: 0")
        print("Lines written: 0")
        print(f"Output file: {out_path}")
        return

    total_valid_scanned = 0
    lines_written = 0
    output_lines = []

    with LOG_FILE.open("r", encoding="utf-8", errors="replace") as fin:
        for line in fin:
            parsed = parse_line(line)
            if parsed is None:
                continue
            timestamp, level, service, message = parsed
            level_up = level.upper()
            if level_up not in ALLOWED_LEVELS:
                continue
            total_valid_scanned += 1
            if matches_filters(level_up, service, level_filter, service_filter):
                output_lines.append(f"{timestamp} | {level_up} | {service} | {message}")
                lines_written += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(output_lines) + ("\n" if output_lines else ""), encoding="utf-8")

    print(f"Valid lines scanned: {total_valid_scanned}")
    print(f"Lines written: {lines_written}")
    print(f"Output file: {out_path}")


if __name__ == "__main__":
    main()
