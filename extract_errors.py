import argparse
from datetime import datetime
import os
import re
import sys


LOG_TIMESTAMP_REGEX = re.compile(r"^(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})(?:,(\d+))?")


def parse_datetime_input(val_str: str, is_end_bound: bool = False) -> datetime:
    """Parse flexible date/time string inputs.

    Supported formats:
      - YYYY-MM-DD
      - YYYY-MM-DD HH (or YYYY-MM-DDTHH)
      - YYYY-MM-DD HH:MM (or YYYY-MM-DDTHH:MM)
      - YYYY-MM-DD HH:MM:SS (or YYYY-MM-DDTHH:MM:SS)
    """
    s = val_str.strip().replace("T", " ")

    formats = [
        ("%Y-%m-%d %H:%M:%S", lambda dt: dt if not is_end_bound else dt.replace(microsecond=999999)),
        ("%Y-%m-%d %H:%M", lambda dt: dt if not is_end_bound else dt.replace(second=59, microsecond=999999)),
        ("%Y-%m-%d %H", lambda dt: dt if not is_end_bound else dt.replace(minute=59, second=59, microsecond=999999)),
        ("%Y-%m-%d", lambda dt: dt if not is_end_bound else dt.replace(hour=23, minute=59, second=59, microsecond=999999)),
    ]

    for fmt, adjust_end in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return adjust_end(dt)
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date/time format: '{val_str}'. "
        "Expected YYYY-MM-DD, 'YYYY-MM-DD HH', 'YYYY-MM-DD HH:MM', or 'YYYY-MM-DD HH:MM:SS'."
    )


def extract_logs_by_range(
    log_file_path: str,
    output_file_path: str,
    start_dt: datetime,
    end_dt: datetime,
) -> int:
    """Extract log entries between `start_dt` and `end_dt` (inclusive)

    and save them into `output_file_path`. Multiline entry lines (e.g. tracebacks)
    are included with their parent log event.
    """
    if not os.path.exists(log_file_path):
        print(f"Error: Input log file '{log_file_path}' does not exist.")
        return 0

    extracted_lines = []
    current_entry_matches = False
    matching_lines_count = 0

    with open(log_file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = LOG_TIMESTAMP_REGEX.match(line)
            if match:
                dt_str = match.group(1).replace("T", " ")
                try:
                    line_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    if start_dt <= line_dt <= end_dt:
                        current_entry_matches = True
                        extracted_lines.append(line)
                        matching_lines_count += 1
                    else:
                        current_entry_matches = False
                except ValueError:
                    current_entry_matches = False
            else:
                if current_entry_matches:
                    extracted_lines.append(line)
                    matching_lines_count += 1

    output_dir = os.path.dirname(output_file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.writelines(extracted_lines)

    start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"Successfully extracted {matching_lines_count} lines matching time range "
        f"[{start_str} -> {end_str}] from '{log_file_path}' into '{output_file_path}'."
    )
    return matching_lines_count


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract worker log entries from worker_errors.log into todo_errors.txt "
            "by specific date/hour, date range, or from a start date until now."
        )
    )

    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help=(
            "Single date or datetime filter (e.g., '2026-08-02', '2026-08-02 17', or '2026-08-02 17:21'). "
            "Defaults to today's date if no range flags are specified."
        ),
    )
    parser.add_argument(
        "-f",
        "--from",
        dest="from_date",
        help="Start date/time for range filter (e.g. '2026-06-04' or '2026-06-04 12:00').",
    )
    parser.add_argument(
        "-t",
        "--to",
        dest="to_date",
        help="End date/time for range filter (e.g. '2026-08-02' or '2026-08-02 18:00').",
    )
    parser.add_argument(
        "--till-now",
        "--to-now",
        action="store_true",
        dest="till_now",
        help="Filter from start date/time until the current moment.",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="logs/worker_errors.log",
        help="Input log file path (default: logs/worker_errors.log)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="links/todo_errors.txt",
        help="Output file path (default: links/todo_errors.txt)",
    )

    args = parser.parse_args()

    try:
        # Determine start_dt and end_dt
        if args.from_date:
            start_dt = parse_datetime_input(args.from_date, is_end_bound=False)
            if args.till_now or not args.to_date:
                end_dt = datetime.now()
            else:
                end_dt = parse_datetime_input(args.to_date, is_end_bound=True)
        elif args.query:
            start_dt = parse_datetime_input(args.query, is_end_bound=False)
            if args.till_now:
                end_dt = datetime.now()
            else:
                end_dt = parse_datetime_input(args.query, is_end_bound=True)
        else:
            # Default to today's date
            today_str = datetime.now().strftime("%Y-%m-%d")
            start_dt = parse_datetime_input(today_str, is_end_bound=False)
            end_dt = datetime.now() if args.till_now else parse_datetime_input(today_str, is_end_bound=True)

        if start_dt > end_dt:
            print(f"Error: Start datetime ({start_dt}) is after end datetime ({end_dt}).")
            sys.exit(1)

        extract_logs_by_range(args.input, args.output, start_dt, end_dt)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
