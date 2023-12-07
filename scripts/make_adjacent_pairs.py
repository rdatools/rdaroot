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

from typing import List, Dict, Tuple

from rdabase import read_json, Graph, mkAdjacencies


def main() -> None:
    """Convert a node/neighbors graph to pairs of adjacent precincts."""

    args: Namespace = parse_args()

    ### READ THE GRAPH JSON ###

    graph_data: Dict[str, List[str]] = read_json(args.graph)

    ### CONVERT IT TO PAIRS OF ADJACENT PRECINCTS ###

    graph: Graph = Graph(graph_data)
    adjacencies: List[Tuple[str, str]] = mkAdjacencies(graph)

    # abs_path: str = FileSpec(args.pairs).abs_path

    with open(args.pairs, "w") as f:
        for one, two in adjacencies:
            print(f"{one},{two}", file=f)


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Convert a node/neighbors graph to pairs of adjacent precincts."
    )

    parser.add_argument(
        "-g",
        "--graph",
        required=True,
        help="Path to the input graph.json",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--pairs",
        required=True,
        help="Path to the output adjacencies.csv",
        type=str,
    )

    args: Namespace = parser.parse_args()

    return args


if __name__ == "__main__":
    main()

### END ###
