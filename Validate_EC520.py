#!/usr/bin/env python3

import argparse
import csv
import sys

# Unit-of-day values >= 500 indicate EC520; values < 500 indicate EC520-W.
EC520_W_UNIT_OF_DAY_THRESHOLD = 500


def is_ec520_w(unit_of_day):
    """Return True for EC520-W serials, False for EC520, based on unit-of-day."""
    try:
        value = int(unit_of_day, 10)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid unit of day: {unit_of_day}") from exc
    return value < EC520_W_UNIT_OF_DAY_THRESHOLD


def scan_csv(file_path):
    matching_ec520_w_rows = {}
    matching_ec520_rows = {}

    with open(file_path, mode="r", newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        print("Scanning file...", file=sys.stderr)

        for row in csv_reader:
            if len(row) < 4:
                continue

            device_name = row[1]
            hardware_id = row[2]
            service_title = row[3]

            if service_title != "Bulk Service":
                continue

            if device_name.startswith("EC520-W-"):
                matching_ec520_w_rows[device_name] = row
                if ":" in hardware_id:
                    print(row)
            elif device_name.startswith("EC520-"):
                matching_ec520_rows[device_name] = row
                if ":" in hardware_id:
                    print(row)

    if matching_ec520_rows or matching_ec520_w_rows:
        print("Matching rows found:", file=sys.stderr)

        for full_serial in matching_ec520_rows:
            serial = full_serial[6:]
            unit_of_day = full_serial[11:14]
            if is_ec520_w(unit_of_day):
                duplicate = "EC520-W-" + serial
                if duplicate in matching_ec520_w_rows:
                    print(
                        "*** EC520-W registered as a EC520, {} has a correct dup. Unit of Day {}".format(
                            full_serial, unit_of_day
                        )
                    )
                    print(matching_ec520_rows[full_serial])
                    print(matching_ec520_w_rows[duplicate])

        for full_serial in matching_ec520_w_rows:
            serial = full_serial[8:]
            unit_of_day = full_serial[13:16]
            if not is_ec520_w(unit_of_day):
                duplicate = "EC520-" + serial
                if duplicate in matching_ec520_rows:
                    print(
                        "*** EC520 registered as a EC520-W, {} has a correct dup. Unit of Day {}".format(
                            full_serial, unit_of_day
                        )
                    )
                    print("   ", matching_ec520_w_rows[full_serial])
                    print("   ", matching_ec520_rows[duplicate])
    else:
        print("No matching rows found.", file=sys.stderr)

    print(
        "Total EC520s {} EC520-W {}".format(
            len(matching_ec520_rows), len(matching_ec520_w_rows)
        ),
        file=sys.stderr,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Validate EC520 and EC520-W device registrations in a DeviceList CSV."
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default="DeviceList.csv",
        help="Path to DeviceList.csv (default: DeviceList.csv in the current directory)",
    )
    args = parser.parse_args()

    try:
        scan_csv(args.file_path)
    except FileNotFoundError:
        print(f"Error: File '{args.file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"An error occurred: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
