#!/usr/bin/env python3
from __future__ import annotations

import argparse
import calendar
from dataclasses import dataclass
from datetime import date


def add_calendar_months(d: date, months: int) -> date:
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(d.day, last_day)
    return date(year, month, day)


@dataclass
class Deadlines:
    received: date
    standard_deadline: date
    extended_deadline: date


def calculate(received: date) -> Deadlines:
    standard = add_calendar_months(received, 1)
    extended = add_calendar_months(received, 3)
    return Deadlines(received=received, standard_deadline=standard, extended_deadline=extended)


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate UK GDPR DSAR response deadlines.")
    parser.add_argument("received", help="Date received in ISO format: YYYY-MM-DD")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    received = date.fromisoformat(args.received)
    d = calculate(received)

    if args.json:
        print(
            "{" +
            f'"received":"{d.received.isoformat()}",' +
            f'"standard_deadline":"{d.standard_deadline.isoformat()}",' +
            f'"extended_deadline":"{d.extended_deadline.isoformat()}"' +
            "}"
        )
    else:
        print(f"Received:           {d.received.isoformat()}")
        print(f"Standard deadline:  {d.standard_deadline.isoformat()}")
        print(f"Extended deadline:  {d.extended_deadline.isoformat()}  (if a lawful 2-month extension is invoked)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
