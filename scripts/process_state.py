#!/usr/bin/env python3

"""
PROCESS A STATE

To run:

$ scripts/process_state.py -s NC

For documentation, type:

$ scripts/process_state.py -h

TODO - Convert this to a shell script <<< Todd

"""

import argparse
from argparse import ArgumentParser, Namespace

import os
from typing import List


def main() -> None:
    """Preprocess the data & find a root map for a state."""

    args: Namespace = parse_args()

    xx: str = args.state

    verbose: bool = args.verbose

    #

    commands: List[str] = [
        "scripts/make_points_file.py -d ../rdadata/data/{xx}/{xx}_2020_data.csv -s ../rdadata/data/{xx}/{xx}_2020_shapes_simplified.json -p temp/{xx}_2020_points.csv",
        "scripts/make_adjacent_pairs.py -g ../rdadata/data/{xx}/{xx}_2020_graph.json -p temp/{xx}_2020_adjacencies.csv",
        "scripts/approx_root.py -s {xx} -p temp/{xx}_2020_points.csv -a temp/{xx}_2020_adjacencies.csv",
    ]

    for command in commands:
        command = command.format(xx=xx)
        os.system(command)


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Preprocess the data & find a root map for a state."
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
