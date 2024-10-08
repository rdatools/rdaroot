#!/usr/bin/env python3

"""
FIND AN APPROXIMATE ROOT MAP FOR A STATE
Given an ensemble of contiguos & roughly equal population maps
as starting points, find a map with the lowest energy.

For example:

$ scripts/approx_root_map.py \
--state NC \
--plans ../../iCloud/fileout/ensembles/MD20U_RMfRST_100_plans.json \
--data ../rdabase/data/MD/MD_2020_data.csv \
--shapes ../rdabase/data/MD/MD_2020_shapes_simplified.json \
--graph ../rdabase/data/MD/MD_2020_graph.json \
--map ../../iCloud/fileout/root_maps/MD20U_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/MD20U_rootcandidates.json \
--log ../../iCloud/fileout/root_maps/MD20U_rootlog.txt \
--no-debug

For documentation, type:

$ scripts/approx_root_map.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace
from typing import Any, List, Dict

import warnings

warnings.warn = lambda *args, **kwargs: None

from collections import defaultdict

from rdabase import (
    require_args,
    read_json,
    write_json,
    Assignment,
    load_data,
    load_shapes,
    load_graph,
    load_metadata,
    is_connected,
)
from rdadccvt import write_redistricting_assignments
from rdaensemble import shared_metadata, plan_from_ensemble
from rdaroot import minimize_energies, plan_is_well_formed


def main() -> None:
    """Find an approximate root map for a state."""

    args: Namespace = parse_args()

    data: Dict[str, Dict[str, int | str]] = load_data(args.data)
    shapes: Dict[str, Any] = load_shapes(args.shapes)
    graph: Dict[str, List[str]] = load_graph(args.graph)
    metadata: Dict[str, Any] = load_metadata(args.state, args.data)

    ensemble: Dict[str, Any] = read_json(args.plans)
    plans: List[Dict[str, str | float | Dict[str, int | str]]] = ensemble["plans"]

    ### DEBUG: VERIFY THAT ALL THE INPUT PLANS ARE WELL FORMED
    if args.debug:
        print()
        print("Verifying that all input plans are complete & contiguous:")
        print()
        for p in plans:
            plan_name: str = str(p["name"])
            assignments: List[Assignment] = [Assignment(k, v) for k, v in p["plan"].items()]  # type: ignore
            well_formed: bool = plan_is_well_formed(plan_name, assignments, data, graph)
            if not well_formed:
                print("This input plan is not well formed.")
                print()
                assert False

        print("All input plans are complete & contiguous.")
        print()
    ###

    with open(args.log, "w") as f:
        min_energy_ensemble: Dict[str, Any] = minimize_energies(
            plans,
            data,
            shapes,
            graph,
            metadata,
            f,
            verbose=args.verbose,
            debug=args.debug,
        )

    lowest_plan: Dict[str, str | float | Dict[str, int | str]] = plan_from_ensemble(
        min_energy_ensemble["lowest_plan"], min_energy_ensemble
    )
    lowest_plan_dict: Dict[str, int | str] = lowest_plan["plan"]  # type: ignore
    assignments: List[Assignment] = [
        Assignment(geoid, district) for geoid, district in lowest_plan_dict.items()
    ]
    write_redistricting_assignments(args.map, assignments)

    min_energy_props: Dict[str, Any] = shared_metadata(args.state, "rdatools/rdaroot")
    # TODO - Update the 'plan_type' property with the arg provided (a bit of a hack ...)
    min_energy_props["packed"] = False
    min_energy_props["discards"] = ensemble["size"] - min_energy_ensemble["size"]
    min_energy_ensemble = min_energy_props | min_energy_ensemble
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
        # "state": "NC",
        # "plans": "../rdaensemble/temp/NC20U_100_plans.json",
        # "data": "../rdabase/data/NC/NC_2020_data.csv",
        # "shapes": "../rdabase/data/NC/NC_2020_shapes_simplified.json",
        # "graph": "../rdabase/data/NC/NC_2020_graph.json",
        # "map": "temp/NC20U_root_map.csv",
        # "candidates": "temp/NC20U_root_candidates.json",
        # "log": "temp/NC20U_root_log.txt",
        #
        # "state": "MD",
        # "plans": "../rdaensemble/temp/MD20U_100_plans.json",
        # "data": "../rdabase/data/MD/MD_2020_data.csv",
        # "shapes": "../rdabase/data/MD/MD_2020_shapes_simplified.json",
        # "graph": "../rdabase/data/MD/MD_2020_graph.json",
        # "map": "temp/MD20U_root_map.csv",
        # "candidates": "temp/MD20U_root_candidates.json",
        # "log": "temp/MD20U_root_log.txt",
        #
        # "state": "PA",
        # "plans": "../../iCloud/fileout/root_maps/PA20C_plans.json",
        # "data": "../rdabase/data/PA/PA_2020_data.csv",
        # "shapes": "../rdabase/data/PA/PA_2020_shapes_simplified.json",
        # "graph": "../rdabase/data/PA/PA_2020_graph.json",
        # "map": "temp/PA20C_root_map.csv",
        # "candidates": "temp/PA20C_root_candidates.json",
        # "log": "temp/PA20C_root_log.txt",
        #
        "state": "MD",
        "plans": "../rdaensemble/temp/MD20C_100_plans.json",
        "data": "../rdabase/data/MD/MD_2020_data.csv",
        "shapes": "../rdabase/data/MD/MD_2020_shapes_simplified.json",
        "graph": "../rdabase/data/MD/MD_2020_graph.json",
        "map": "temp/MD20C_root_map.csv",
        "candidates": "temp/MD20C_root_candidates.json",
        "log": "temp/MD20C_root_log.txt",
        "verbose": True,
    }
    args = require_args(args, args.debug, debug_defaults)

    return args


if __name__ == "__main__":
    main()

### END ###
