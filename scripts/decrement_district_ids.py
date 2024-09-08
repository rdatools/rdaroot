#!/usr/bin/env python3

"""
DECREMENT DISTRICT IDS TO FOR A CSV PLAN

For example:

$ scripts/decrement_district_ids.py \
--input ../tradeoffs/root_maps/NC20U_root_map_from_DRA.csv \
--output ../tradeoffs/root_maps/NC20U_root_map.csv

For documentation, type:

$ scripts/decrement_district_ids.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace
from typing import Any, List, Dict

from rdabase import (
    require_args,
    read_csv,
    write_csv,
)


def main() -> None:
    args: argparse.Namespace = parse_args()

    input_plan: List[Dict[str, str | int]] = read_csv(args.input, [str, int])

    output_plan: List[Dict[str, str | int]] = [
        {"GEOID": a["GEOID"], "DISTRICT": int(a["DISTRICT"]) - 1} for a in input_plan
    ]

    write_csv(args.output, output_plan, ["GEOID", "DISTRICT"])


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Decrement district IDs to start at zero"
    )

    parser.add_argument(
        "--input",
        help="The path to the input plan with district IDs starting at 1",
        type=str,
    )
    parser.add_argument(
        "--output",
        help="The path to the output plan with district IDs starting at 0",
        type=str,
    )
    # Enable debug/explicit mode
    parser.add_argument("--debug", default=True, action="store_true", help="Debug mode")
    parser.add_argument(
        "--no-debug", dest="debug", action="store_false", help="Explicit mode"
    )

    args: Namespace = parser.parse_args()

    # Default values for args in debug mode
    debug_defaults: Dict[str, Any] = {
        "input": "../tradeoffs/root_maps/NC20U_root_map_from_DRA.csv",
        "output": "../tradeoffs/root_maps/NC20U_root_map.csv",
    }
    args = require_args(args, args.debug, debug_defaults)

    return args


if __name__ == "__main__":
    main()

### END ###
