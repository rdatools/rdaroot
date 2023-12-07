#!/usr/bin/env python3
#

"""
GENERATE A SET OF RANDOM MAPS
using Heuristic 1.

For example:

$ scripts/generate_random_maps.py -s NC -p temp/NC_2020_points.csv -a temp/NC_2020_adjacencies.csv
$ scripts/generate_random_maps.py -s NC -p temp/NC_2020_points.csv -a temp/NC_2020_adjacencies.csv -i 10
$ scripts/generate_random_maps.py -s NC -p temp/NC_2020_points.csv -a temp/NC_2020_adjacencies.csv -u

For documentation, type:

$ scripts/generate_random_maps.py -h

TODO

"""

import argparse
from argparse import ArgumentParser, Namespace

from typing import Any, List, Dict, Tuple, Set

import os

from rdabase import (
    cycle,
    DISTRICTS_BY_STATE,
    starting_seed,
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
    dccvt_randommap,
    dccvt_initial,
    dccvt_points,
    file_list,
    clean,
    read_redistricting_points,
    read_redistricting_pairs,
    index_points_file,
    index_pairs_file,
    index_assignments_file,
    random_map,
    calc_energy_file,
    calc_population_deviation_file,
)


def main() -> None:
    """Generate an ensemble of random maps for a state."""

    args: Namespace = parse_args()

    xx: str = args.xx
    precincts: str = args.points
    adjacencies: str = args.adjacencies
    iterations: int = args.iterations
    unsimplified: bool = args.unsimplified

    verbose: bool = args.verbose

    ### DEBUG ###

    ### SETUP FOR ITERATIONS ###

    random_scores: str = "maps/" + f"{xx}_{cycle}_random_maps_{iterations}_scores.csv"
    random_candidates: str = (
        "maps/" + f"{xx}_{cycle}_random_maps_{iterations}_plans.json"
    )
    random_log: str = "maps/" + f"{xx}_{cycle}_random_maps_{iterations}_log.txt"

    N: int = DISTRICTS_BY_STATE[xx]["congress"]
    start: int = starting_seed(xx, N)

    # Read the input points & adjacencies & index them by GEOID offset.
    points_csv: str = os.path.abspath(precincts)
    adjacencies_csv: str = os.path.abspath(adjacencies)
    if unsimplified:  # NOTE - Use unsimplified points & adjacencies.
        points_csv = os.path.abspath("testdata/NC/baseline.data.input.csv")
        adjacencies_csv = os.path.abspath("testdata/NC/baseline.adjacencies.input.csv")
    points: List[Point] = read_redistricting_points(points_csv)
    pairs: List[Tuple[str, str]] = read_redistricting_pairs(adjacencies_csv)
    index_points_file(points, dccvt_points, verbose=verbose)
    # index_pairs_file(points, pairs, dccvt_adjacencies, verbose=verbose)

    # Gather populations by GEOID for energy calculations & offset them by GEOID for indexing initial assignments.
    populations: Dict[str, int] = {p.geoid: int(p.pop) for p in points}
    total_pop: int = sum(populations.values())
    index_by_geoid: Dict[str, int] = {p.geoid: i for i, p in enumerate(points)}  # TODO

    ### SETUP FOR SCORING ###

    data_path: str = f"../rdabase/data/{xx}/{xx}_2020_data.csv"
    shapes_path: str = f"../rdabase/data/{xx}/{xx}_2020_shapes_simplified.json"
    graph_path: str = f"../rdabase/data/{xx}/{xx}_2020_graph.json"

    data: Dict[str, Dict[str, str | int]] = load_data(data_path)
    shapes: Dict[str, Any] = load_shapes(shapes_path)
    graph: Dict[str, List[str]] = load_graph(graph_path)
    metadata: Dict[str, Any] = load_metadata(xx, data_path)

    ### LOOP FOR THE SPECIFIED NUMBER OF CONFORMING CANDIDATES ###

    scores: List[Dict[str, Any]] = list()
    candidates: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    conforming_count: int = 0
    seed: int = start

    with open(random_log, "a") as f:
        while True:
            print(f"... {conforming_count} ...")
            print(f"Conforming count: {conforming_count}, random seed: {seed}", file=f)

            label: str = f"{conforming_count:03d}_{seed}"
            clean(file_list)

            try:
                # Generate a random contiguous & 'roughly' equal population partitioning of the state.
                random_map(
                    pairs,
                    populations,
                    N,
                    seed,
                    dccvt_randommap,
                )
                # Index those assignments by GEOID & district offset.
                index_assignments_file(
                    dccvt_randommap,
                    index_by_geoid,
                    populations,
                    dccvt_initial,
                    verbose=verbose,
                )

                # Calculate the energy & population deviation of the map.
                energy: float = calc_energy_file(dccvt_initial, dccvt_points)
                popdev: float = calc_population_deviation_file(
                    dccvt_randommap, populations, total_pop, N
                )

                # If the map does not have 'roughly' equal population, discard it.
                if popdev > args.roughlyequal:
                    continue

                # Otherwise increment candidate count, save the plan, & score it.
                conforming_count += 1
                assignments: List[Assignment] = load_plan(dccvt_randommap)

                plan: Dict[str, int | str] = {a.geoid: a.district for a in assignments}
                # plan: Dict[str, int] = {
                #     str(a["GEOID"]): int(a["DISTRICT"]) for a in assignments
                # }
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

                # If the conforming candidate count equal to the number of iterations, stop.
                if conforming_count == iterations:
                    break

            except Exception as e:
                print(f"Failure: {e}", file=f)
                pass

            finally:
                seed += 1

        print(
            f"{conforming_count} conforming candidates took {seed - start + 1} random seeds.",
            file=f,
        )

    ### SAVE THE CANDIDATE MAPS & THEIR SCORES ###

    write_json(random_candidates, candidates)

    fields: List[str] = list(scores[0].keys())
    write_csv(random_scores, scores, fields, precision="{:.6f}")


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Generate an ensemble of random maps for a state."
    )

    parser.add_argument(
        "-s",
        "--xx",
        default="NC",
        help="The two-character state code (e.g., NC)",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--points",
        default="temp/NC_2020_points.csv",
        help="Path to the input points.csv",
        type=str,
    )
    parser.add_argument(
        "-a",
        "--adjacencies",
        default="temp/NC_2020_adjacencies.csv",
        help="Path to the input adjacencies.csv",
        type=str,
    )
    parser.add_argument(
        "-i",
        "--iterations",
        default=1000,
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
        "-u",
        "--unsimplified",
        dest="unsimplified",
        action="store_true",
        help="Use unsimplified points & adjacencies",
    )

    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
    )

    args: Namespace = parser.parse_args()
    return args


if __name__ == "__main__":
    main()

### END ###
