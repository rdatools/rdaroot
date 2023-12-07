#!/usr/bin/env python3
#

"""
FIND AN APPROXIMATE ROOT MAP FOR A STATE
using random district centroids as the starting points
and some front-end transformations before the Balzer algorithm (DCCVT).

NOTE - This should closely approximate our original 'baseline' approach.

For example:

scripts/root_map_heuristic_2.py \
    --state NC \
    --data ../rdadata/data/NC/NC_2020_data.csv \
    --shapes ../rdadata/data/NC/NC_2020_shapes_simplified.json \
    --graph ../rdadata/data/NC/NC_2020_graph.json \
    --points temp/NC_2020_points.csv \
    --adjacencies temp/NC_2020_adjacencies.csv \
    --map output/NC_2020_root_map.csv \
    --candidates output/NC_2020_root_candidates.json \
    --scores output/NC_2020_root_scores.csv \
    --log output/NC_2020_root_log.txt \
    --explicit

For documentation, type:

$ scripts/root_map_heuristic_2.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace
from typing import Any, List, Dict, Tuple

import shutil

from rdabase import (
    require_args,
    DISTRICTS_BY_STATE,
    starting_seed,
    populations,
    total_population,
    write_csv,
    write_json,
    Point,
    Assignment,
)
from rdascore import (
    load_data,
    load_shapes,
    load_graph,
    load_metadata,
    load_plan,
    analyze_plan,
)
from rdaroot import (
    file_list,
    clean,
    dccvt_randomsites,
    dccvt_initial,
    dccvt_points,
    dccvt_adjacencies,
    dccvt_balzer1,
    dccvt_contiguous,
    dccvt_balzer2,
    dccvt_consolidated,
    dccvt_complete,
    dccvt_output,
    read_redistricting_points,
    read_redistricting_pairs,
    index_points_file,
    index_pairs_file,
    randomsites,
    initial,
    balzer_go,
    mk_contiguous,
    consolidate,
    complete,
    postprocess,
    calc_energy_file,
    calc_population_deviation_file,
)


def main() -> None:
    """Find an approximate root map for a state."""

    args: Namespace = parse_args()

    ### SETUP FOR SCORING ###

    data: Dict[str, Dict[str, int | str]] = load_data(args.data)
    shapes: Dict[str, Any] = load_shapes(args.shapes)
    graph: Dict[str, list[str]] = load_graph(args.graph)
    metadata: Dict[str, Any] = load_metadata(args.state, args.data)

    ### SETUP FOR ITERATIONS ###

    clean(file_list)

    N: int = DISTRICTS_BY_STATE[args.state]["congress"]
    start: int = starting_seed(args.state, N)

    points: List[Point] = read_redistricting_points(args.points)  # must exist
    pairs: List[Tuple[str, str]] = read_redistricting_pairs(args.adjacencies)  # ditto

    index_points_file(points, dccvt_points, verbose=args.verbose)
    index_pairs_file(points, pairs, dccvt_adjacencies, verbose=args.verbose)

    pop_by_geoid: Dict[str, int] = populations(data)
    total_pop: int = total_population(pop_by_geoid)

    ### LOOP FOR THE SPECIFIED NUMBER OF CONFORMING CANDIDATES ###

    lowest_energy: float = float("inf")
    scores: List[Dict[str, Any]] = list()
    candidates: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    conforming_count: int = 0
    seed: int = start

    with open(args.log, "a") as f:
        while True:
            print(f"... {conforming_count} ...")
            print(f"Conforming count: {conforming_count}, random seed: {seed}", file=f)

            label: str = f"{conforming_count:03d}_{seed}"
            clean(file_list)

            try:
                # Get random sites from the input points (precincts).
                randomsites(dccvt_points, dccvt_randomsites, N, seed)

                # Make initial assignments of precincts (points) to districts (sites).
                initial(dccvt_randomsites, dccvt_points, dccvt_initial)

                # Run Balzer's algorithm (DCCVT) to get balanced but not contiguous assignments.
                balzer_go(
                    dccvt_points,
                    None,  # NOTE - No adjacencies for the initial run.
                    dccvt_initial,
                    dccvt_balzer1,
                    balance=False,
                )

                # Make them contiguous but not balanced.
                mk_contiguous(dccvt_balzer1, dccvt_adjacencies, dccvt_contiguous)

                # Run Balzer's algorithm again to get balanced & contiguous assignments.
                balzer_go(
                    dccvt_points,
                    dccvt_adjacencies,
                    dccvt_contiguous,
                    dccvt_balzer2,
                    balance=True,
                )

                # Clean up the Balzer assignments, unsplitting any precincts that were split.
                consolidate(
                    dccvt_balzer2,
                    dccvt_adjacencies,
                    label,
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
                    dccvt_complete, args.points, dccvt_output, verbose=args.verbose
                )

                # Calculate the energy & population deviation of the map.
                energy: float = calc_energy_file(dccvt_complete, dccvt_points)
                popdev: float = calc_population_deviation_file(
                    dccvt_output, pop_by_geoid, total_pop, N
                )

                # If the map does not have 'roughly' equal population, discard it.
                if popdev > args.roughlyequal:
                    continue

                # Otherwise increment candidate count, save the plan, & score it.
                conforming_count += 1
                assignments: List[Assignment] = load_plan(dccvt_output)

                plan: Dict[str, int | str] = {a.geoid: a.district for a in assignments}
                candidates.append({"name": label, "plan": plan})  # No weights.

                record: Dict[str, Any] = dict()
                record["map"] = label
                record["energy"] = energy

                scorecard: Dict[str, Any] = analyze_plan(
                    assignments,
                    data,
                    shapes,
                    graph,
                    metadata,
                )
                record.update(scorecard)
                scores.append(record)

                # If the energy is less than the best energy so far, save the map as the best map so far.
                if energy < lowest_energy:
                    lowest_energy = energy
                    shutil.copy(dccvt_output, args.map)

                # If the conforming candidate count equal to the number of iterations, stop.
                if conforming_count == args.iterations:
                    break

            except Exception as e:
                print(f"Failure: {e}", file=f)
                continue

            finally:
                seed += 1

        print(
            f"{conforming_count} conforming candidates took {seed - start + 1} random seeds.",
            file=f,
        )

    ### SAVE THE CANDIDATE MAPS & THEIR SCORES ###

    write_json(args.candidates, candidates)

    fields: List[str] = list(scores[0].keys())
    write_csv(args.scores, scores, fields, precision="{:.6f}")


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
        "--points",
        help="Path to the input points.csv",
        type=str,
    )
    parser.add_argument(
        "--adjacencies",
        help="Path to the input adjacencies.csv",
        type=str,
    )
    parser.add_argument(
        "--map",
        help="Path to the output map.csv",
        type=str,
    )
    parser.add_argument(
        "--candidates",
        help="Path to the output candidates.json",
        type=str,
    )
    parser.add_argument(
        "--scores",
        default="output/NC_2020_root_scores.csv",
        help="Path to the output scores.csv",
        type=str,
    )
    parser.add_argument(
        "--log",
        default="output/log.txt",
        help="Path to the output log.txt",
        type=str,
    )
    parser.add_argument(
        "-i",
        "--iterations",
        default=100,
        help="The number of conforming candidates to evaluate.",
        type=int,
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
        "--explicit", dest="debug", action="store_false", help="Explicit mode"
    )

    args: Namespace = parser.parse_args()

    # Default values for args in debug mode
    debug_defaults: Dict[str, Any] = {
        "state": "NC",
        "data": "../rdadata/data/NC/NC_2020_data.csv",
        "shapes": "../rdadata/data/NC/NC_2020_shapes_simplified.json",
        "graph": "../rdadata/data/NC/NC_2020_graph.json",
        "points": "temp/NC_2020_points.csv",
        "adjacencies": "temp/NC_2020_adjacencies.csv",
        "map": "output/NC_2020_root_map.csv",
        "candidates": "output/NC_2020_root_candidates.json",
        "scores": "output/NC_2020_root_scores.csv",
    }
    args = require_args(args, args.debug, debug_defaults)

    return args


if __name__ == "__main__":
    main()

### END ###
