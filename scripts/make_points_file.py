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

import os
from typing import Any, List, Dict

import rdabase as rdautils


def main() -> None:
    """Join the census & election data for a state and index it by GEOID."""

    args: Namespace = parse_args()

    data_path: str = os.path.abspath(args.data)
    shapes_path: str = os.path.abspath(args.shapes)
    points_path: str = os.path.abspath(args.points)

    verbose: bool = args.verbose

    ### READ THE PRECINT DATA ###

    data: List[Dict[str, str | int]] = rdautils.read_csv(data_path, [str] + [int] * 13)

    ### READ THE SHAPES DATA ###

    shapes: Dict[str, Any] = rdautils.read_json(shapes_path)

    ### JOIN THEM BY GEOID & SUBSET THE FIELDS ###

    points: List[Dict] = list()

    for row in data:
        point = dict()
        geoid: str = str(row[rdautils.geoid_field])

        point["GEOID"] = geoid
        point["POP"] = row["TOTAL_POP"]
        point["X"] = shapes[geoid]["center"][0]
        point["Y"] = shapes[geoid]["center"][1]

        points.append(point)

    ### WRITE THE COMBINED DATA AS A CSV ###

    rdautils.write_csv(
        points_path, points, ["GEOID", "POP", "X", "Y"], precision="{:.14f}"
    )


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

    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
    )

    args: Namespace = parser.parse_args()
    return args


if __name__ == "__main__":
    main()

### END ###
