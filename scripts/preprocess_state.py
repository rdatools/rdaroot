#!/usr/bin/env python3

"""
PRE-PROCESS DATA & SHAPES FOR A STATE

To run:

$ scripts/preprocess_state.py -s NC

For documentation, type:

$ scripts/preprocess_state.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace

import os
from typing import List


def main() -> None:
    """Preprocess the data & shapes for a state."""

    args: Namespace = parse_args()

    verbose: bool = args.verbose

    #

    commands: List[str] = [
        "scripts/make_points_file.py -d ../rdabase/data/{xx}/{xx}_2020_data.csv -s ../rdabase/data/{xx}/{xx}_2020_shapes_simplified.json -p temp/{xx}_2020_points.csv",
        "scripts/make_adjacent_pairs.py -g ../rdabase/data/{xx}/{xx}_2020_graph.json -p temp/{xx}_2020_adjacencies.csv",
    ]

    for command in commands:
        command = command.format(xx=args.state)
        os.system(command)


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Preprocess the data & shapes for a state."
    )

    parser.add_argument(
        "-s",
        "--state",
        default="{xx}",
        help="The two-character state code (e.g., {xx})",
        type=str,
    )

    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
    )

    args: Namespace = parser.parse_args()
    return args


### END ###
