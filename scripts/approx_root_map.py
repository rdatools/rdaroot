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
    --no-debug

For documentation, type:

$ scripts/approx_root_map.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace
from typing import Any, List, Dict, Tuple

import shutil

from uses import *


def main() -> None:
    """Find an approximate root map for a state."""

    args: Namespace = parse_args()

    data: Dict[str, Dict[str, int | str]] = load_data(args.data)
    shapes: Dict[str, Any] = load_shapes(args.shapes)
    # graph: Dict[str, List[str]] = load_graph(args.graph)
    metadata: Dict[str, Any] = load_metadata(args.state, args.data)

    points: List[Point] = mkPoints(data, shapes)

    temp_points: str = "temp/NC20C_points.csv"
    write_redistricting_points(points, temp_points)

    indexed_geoids: Dict[str, int] = index_geoids(points)

    pop_by_geoid: Dict[str, int] = populations(data)
    total_pop: int = total_population(pop_by_geoid)

    ensemble_in: Dict[str, Any] = read_json(args.plans)
    plans_in: List[Dict[str, str | float | Dict[str, int | str]]] = ensemble_in["plans"]

    ensemble_out: Dict[str, Any] = dict()
    # TODO - Add metadata
    plans_out: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    N: int = int(metadata["D"])
    lowest_energy: float = float("inf")

    for i, p in enumerate(plans_in):
        print(f"... {i} ...")

        # Get a plan & make it the initial assignments.
        plan_name: str = str(p["name"])
        clean(file_list)

        plan_dict: Dict[str, int | str] = p["plan"]  # type: ignore
        assignments: List[Assignment] = make_plan(plan_dict)

        try:
            indexed_assignments: List[IndexedWeightedAssignment] = index_assignments(
                assignments, indexed_geoids, pop_by_geoid
            )
            write_assignments(dccvt_initial, indexed_assignments)

            # Run Balzer's algorithm (DCCVT) to get balanced & contiguous assignments.
            balzer_go(
                dccvt_points,
                dccvt_adjacencies,
                dccvt_initial,
                dccvt_balzer2,
                balance=True,
            )

            # Clean up the Balzer assignments, unsplitting any precincts that were split.
            consolidate(
                dccvt_balzer2,
                dccvt_adjacencies,
                plan_name,
                dccvt_consolidated,
                verbose=args.verbose,
            )
            complete(
                dccvt_consolidated,
                dccvt_adjacencies,
                dccvt_points,
                dccvt_complete,
                verbose=args.verbose,
            )

            # De-index Balzer assignments to use GEOIDs.
            postprocess(
                dccvt_complete,
                temp_points,
                dccvt_output,
                verbose=args.verbose,
            )

        except Exception as e:
            print(f"Failure: {e}")
            continue

        # Record the candidate map.
        assignments: List[Assignment] = load_plan(dccvt_output)
        plan: Dict[str, int | str] = {a.geoid: a.district for a in assignments}
        plans_out.append({"name": plan_name, "plan": plan})  # No weights.

        # Calculate the energy & population deviation of the map.
        energy: float = calc_energy_file(dccvt_complete, dccvt_points)
        popdev: float = calc_population_deviation_file(
            dccvt_output, pop_by_geoid, total_pop, N
        )

        # If the map does not have 'roughly' equal population, ignore it.
        if popdev > args.roughlyequal:
            continue

        # If the energy is less than the best energy so far, save the map as the best map so far.
        if energy < lowest_energy:
            lowest_energy = energy
            shutil.copy(dccvt_output, args.map)

    ensemble_out["plans"] = plans_out
    write_json(args.candidates, ensemble_out)


# TODO - Re-factor this into rdabase
def make_plan(assignments: Dict[str, int | str]) -> List[Assignment]:
    """Convert a dict of geoid: district assignments to a list of Assignments."""

    plan: List[Assignment] = [
        Assignment(geoid, district) for geoid, district in assignments.items()
    ]
    return plan


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
        "data": "../rdadata/data/NC/NC20C_data.csv",
        "shapes": "../rdadata/data/NC/NC20C_shapes_simplified.json",
        "graph": "../rdadata/data/NC/NC20C_graph.json",
        "map": "output/NC20C_RMfRST_100_rootmap.csv",
        "candidates": "output/NC20C_RMfRST_100_rootcandidates.json",
    }
    args = require_args(args, args.debug, debug_defaults)

    return args


if __name__ == "__main__":
    main()

### END ###
