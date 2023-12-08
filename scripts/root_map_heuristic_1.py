#!/usr/bin/env python3

"""
FIND AN APPROXIMATE ROOT MAP FOR A STATE
using random contiguous maps with 'roughly' equal population districts as the starting points
for the Balzer algorithm (DCCVT).

For example:

scripts/root_map_heuristic_1.py \
    --state NC \
    --data ../rdadata/data/NC/NC_2020_data.csv \
    --shapes ../rdadata/data/NC/NC_2020_shapes_simplified.json \
    --graph ../rdadata/data/NC/NC_2020_graph.json \
    --points temp/NC_2020_points.csv \
    --adjacencies temp/NC_2020_adjacencies.csv \
    --map output/NC_2020_root_map_1.csv \
    --candidates output/NC_2020_root_candidates_1.json \
    --scores output/NC_2020_root_scores_1.csv \
    --log output/NC_2020_root_log_1.txt \
    --explicit

For documentation, type:

$ scripts/root_map_heuristic_1.py -h

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
    graph: Dict[str, list[str]] = load_graph(args.graph)
    metadata: Dict[str, Any] = load_metadata(args.state, args.data)

    points: List[Point] = mkPoints(data, shapes)
    pairs: List[Tuple[str, str]] = mkAdjacencies(Graph(graph))

    indexed_geoids: Dict[str, int] = index_geoids(points)
    indexed_points: List[IndexedPoint] = index_points(points)

    pop_by_geoid: Dict[str, int] = populations(data)
    total_pop: int = total_population(pop_by_geoid)

    clean(file_list)

    N: int = DISTRICTS_BY_STATE[args.state]["congress"]
    start: int = starting_seed(args.state, N)

    scores: List[Dict[str, Any]] = list()
    candidates: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    conforming_count: int = 0
    seed: int = start
    lowest_energy: float = float("inf")

    with open(args.log, "a") as f:
        while True:
            print(f"... {conforming_count} ...")
            print(f"Conforming count: {conforming_count}, random seed: {seed}", file=f)

            clean(file_list)
            label: str = f"{conforming_count:03d}_{seed}"

            try:
                # Generate a random contiguous & 'roughly' equal population partitioning of the state.
                assignments: List[Assignment] = random_map(
                    pairs,
                    pop_by_geoid,
                    args.districts,
                    seed,
                )
                indexed_assignments: List[
                    IndexedWeightedAssignment
                ] = index_assignments(assignments, indexed_geoids, pop_by_geoid)
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
        "map": "output/NC_2020_root_map_1.csv",
        "candidates": "output/NC_2020_root_candidates_1.json",
        "scores": "output/NC_2020_root_scores_1.csv",
    }
    args = require_args(args, args.debug, debug_defaults)

    return args


if __name__ == "__main__":
    main()

### END ###
