#!/usr/bin/env python3

"""
FIND AN APPROXIMATE ROOT MAP FOR A STATE
Given an ensemble of contiguos & roughly equal population maps
as starting points, find a map with the lowest energy.

For example:

$ scripts/approx_root_map.py \
    --state NC \
    --plans ../rdaensemble/output/NC20C_RMfRST_100_plans.json \
    --data ../rdadata/data/NC/NC_2020_data.csv \
    --shapes ../rdadata/data/NC/NC_2020_shapes_simplified.json \
    --graph ../rdadata/data/NC/NC_2020_graph.json \
    --map output/NC20C_RMfRST_100_rootmap.csv \
    --candidates output/NC20C_RMfRST_100_rootcandidates.json \
    --log output/NC20C_RMfRST_100_rootlog.txt \
    --no-debug

For documentation, type:

$ scripts/approx_root_map.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace
from typing import Any, List, Dict

from rdabase import require_args, read_json, write_json, Assignment
from rdascore import load_data, load_shapes, load_graph, load_metadata, load_plan
from rdaroot import minimize_energies, write_redistricting_assignments


def main() -> None:
    """Find an approximate root map for a state."""

    args: Namespace = parse_args()

    data: Dict[str, Dict[str, int | str]] = load_data(args.data)
    shapes: Dict[str, Any] = load_shapes(args.shapes)
    graph: Dict[str, List[str]] = load_graph(args.graph)
    metadata: Dict[str, Any] = load_metadata(args.state, args.data)

    ensemble: Dict[str, Any] = read_json(args.plans)
    plans: List[Dict[str, str | float | Dict[str, int | str]]] = ensemble["plans"]

    with open(args.log, "w") as f:
        min_energy_ensemble: Dict[str, Any] = minimize_energies(
            plans, data, shapes, graph, metadata, f, verbose=args.verbose
        )

    lowest_plan: Dict[str, int | str] = min_energy_ensemble["plan"]["lowest_plan"]  # type: ignore
    assignments: List[Assignment] = [
        Assignment(geoid, district) for geoid, district in lowest_plan.items()
    ]
    write_redistricting_assignments(args.map, assignments)

    # TODO - Add metadata

    write_json(args.candidates, min_energy_ensemble)


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Find an approximate root map for a state."
    )

    parser.add_argument(
        "--state",
        help="The two-character state code (e.g., NC)",
        type=str,
    )
    parser.add_argument(
        "--plans",
        type=str,
        help="Candidate plans ensemble JSON file",
    )
    parser.add_argument(
        "--data",
        type=str,
        help="Data file",
    )
    parser.add_argument(
        "--shapes",
        type=str,
        help="Shapes abstract file",
    )
    parser.add_argument(
        "--graph",
        type=str,
        help="Graph file",
    )
    parser.add_argument(
        "--map",
        help="Path to the output map.csv",
        type=str,
    )
    parser.add_argument(
        "--candidates",
        type=str,
        help="Candidate plans output ensemble JSON file",
    )
    parser.add_argument(
        "--log",
        type=str,
        help="Log TXT file",
    )
    parser.add_argument(
        "--roughlyequal",
        type=float,
        default=0.02,
        help="'Roughly equal' population threshold",
    )

    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
    )

    # Enable debug/explicit mode
    parser.add_argument("--debug", default=True, action="store_true", help="Debug mode")
    parser.add_argument(
        "--no-debug", dest="debug", action="store_false", help="Explicit mode"
    )

    args: Namespace = parser.parse_args()

    # Default values for args in debug mode
    debug_defaults: Dict[str, Any] = {
        "state": "NC",
        "plans": "../rdaensemble/output/NC20C_RMfRST_100_plans.json",
        "data": "../rdabase/data/NC/NC_2020_data.csv",
        "shapes": "../rdabase/data/NC/NC_2020_shapes_simplified.json",
        "graph": "../rdadata/data/NC/NC_2020_graph.json",
        "map": "output/NC20C_RMfRST_100_rootmap.csv",
        "candidates": "output/NC20C_RMfRST_100_rootcandidates.json",
        "log": "output/NC20C_RMfRST_100_rootlog.json",
    }
    args = require_args(args, args.debug, debug_defaults)

    return args


if __name__ == "__main__":
    main()

### END ###
