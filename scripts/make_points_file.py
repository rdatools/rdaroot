#!/usr/bin/env python3
#

"""
MAKE A POINTS CSV FILE

For example:

$ scripts/make_points_file.py -d ../rdabase/data/NC/NC_2020_data.csv -s ../rdabase/data/NC/NC_2020_shapes_simplified.json -p temp/NC_2020_points.csv

For documentation, type:

$ scripts/make_points_file.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace

from typing import Any, List, Dict

from rdabase import read_csv, read_json, write_csv, Point, index_data, mkPoints


def main() -> None:
    """Join the census & election data for a state and index it by GEOID."""

    args: Namespace = parse_args()

    ### READ THE PRECINT DATA & SHAPES ###

    data: List[Dict[str, str | int]] = read_csv(args.data, [str] + [int] * 13)
    shapes: Dict[str, Any] = read_json(args.shapes)

    ### JOIN THEM BY GEOID & SUBSET THE FIELDS ###

    indexed_data: Dict[str, Dict[str, str | int]] = index_data(data)
    points: List[Point] = mkPoints(indexed_data, shapes)

    ### WRITE THE COMBINED DATA AS A CSV ###

    csv_dict: List[Dict] = [
        {"GEOID": p.geoid, "POP": p.pop, "X": p.ll.long, "Y": p.ll.lat} for p in points
    ]
    write_csv(args.points, csv_dict, ["GEOID", "POP", "X", "Y"], precision="{:.14f}")


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Make a points file for input to the root/baseline code."
    )

    parser.add_argument(
        "-d",
        "--data",
        default="../rdabase/data/NC/NC_2020_data.csv",
        help="Path to the input data.csv",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--shapes",
        default="../rdabase/data/NC/NC_2020_shapes_simplified.json",
        help="Path to the input shapes.json",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--points",
        default="temp/NC_2020_points.csv",
        help="Path to the output points.csv",
        type=str,
    )

    args: Namespace = parser.parse_args()
    return args


if __name__ == "__main__":
    main()

### END ###
