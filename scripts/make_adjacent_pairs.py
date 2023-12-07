#!/usr/bin/env python3
#

"""
CONVERT A GRAPH JSON TO AN ADJACENT PAIRS CSV

For example:

$ scripts/make_adjacent_pairs.py -g ../rdabase/data/NC/NC_2020_graph.json -p temp/NC_2020_adjacencies.csv

For documentation, type:

$ scripts/make_adjacent_pairs.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace

import os
from typing import List, Dict

import rdabase as rdautils


def main() -> None:
    """Convert a node/neighbors graph to pairs of adjacent precincts."""

    args: Namespace = parse_args()

    graph_path: str = os.path.abspath(args.graph)
    pairs_path: str = os.path.abspath(args.pairs)

    verbose: bool = args.verbose

    ### READ THE GRAPH JSON ###

    graph_data: Dict[str, List[str]] = rdautils.read_json(graph_path)

    ### CONVERT IT TO PAIRS OF ADJACENT PRECINCTS ###

    graph: rdautils.Graph = rdautils.Graph(graph_data)

    abs_path: str = rdautils.FileSpec(pairs_path).abs_path

    with open(abs_path, "w") as f:
        for one, two in graph.adjacencies():
            if one != "OUT_OF_STATE" and two != "OUT_OF_STATE":
                print(f"{one},{two}", file=f)

    pass


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Convert a node/neighbors graph to pairs of adjacent precincts."
    )

    parser.add_argument(
        "-g",
        "--graph",
        default="../rdabase/data/NC/NC_2020_graph.json",
        help="Path to the input graph.json",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--pairs",
        default="temp/NC_2020_adjacencies.csv",
        help="Path to the output adjacencies.csv",
        type=str,
    )

    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
    )

    args: Namespace = parser.parse_args()

    return args


if __name__ == "__main__":
    main()

### END ###
