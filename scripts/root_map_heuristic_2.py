#!/usr/bin/env python3
#

"""
FIND AN APPROXIMATE ROOT MAP FOR A STATE
using random district centroids as the starting points
and some front-end transformations before the Balzer algorithm (DCCVT).

NOTE - This should closely approximate our original 'baseline' approach.

For example:

$ scripts/root_map_heuristic_2.py -s NC -p temp/NC_2020_points.csv -a temp/NC_2020_adjacencies.csv
$ scripts/root_map_heuristic_2.py -s NC -p temp/NC_2020_points.csv -a temp/NC_2020_adjacencies.csv -q
$ scripts/root_map_heuristic_2.py -s NC -p temp/NC_2020_points.csv -a temp/NC_2020_adjacencies.csv -q -u

For documentation, type:

$ scripts/root_map_heuristic_2.py -h

"""

import argparse
from argparse import ArgumentParser, Namespace

from typing import Any, List, Dict, Tuple

import os
import shutil

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

    xx: str = args.xx
    precincts: str = args.points
    adjacencies: str = args.adjacencies
    iterations: int = args.iterations
    unsimplified: bool = args.unsimplified
    qualify: bool = args.qualify

    verbose: bool = args.verbose

    ### DEBUG ###

    ### SETUP FOR ITERATIONS ###

    qualifier: str = (
        f"_{iterations}_heuristic2_{'unsimplified' if unsimplified else 'simplified'}"
        if qualify
        else ""
    )
    root_map: str = "output/" + f"{xx}_{cycle}_root_map" + qualifier + ".csv"
    root_scores: str = "output/" + f"{xx}_{cycle}_root_scores" + qualifier + ".csv"
    root_candidates: str = (
        "output/" + f"{xx}_{cycle}_root_candidates" + qualifier + ".json"
    )
    root_log: str = "output/" + f"{xx}_{cycle}_root_log" + qualifier + ".txt"

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
    index_pairs_file(points, pairs, dccvt_adjacencies, verbose=verbose)

    # Gather populations by GEOID for energy calculations.
    populations: Dict[str, int] = {p.geoid: int(p.pop) for p in points}
    total_pop: int = sum(populations.values())

    ### SETUP FOR SCORING ###

    data_path: str = f"../rdabase/data/{xx}/{xx}_2020_data.csv"
    shapes_path: str = f"../rdabase/data/{xx}/{xx}_2020_shapes_simplified.json"
    graph_path: str = f"../rdabase/data/{xx}/{xx}_2020_graph.json"

    data: Dict[str, Dict[str, str | int]] = load_data(data_path)
    shapes: Dict[str, Any] = load_shapes(shapes_path)
    graph: Dict[str, List[str]] = load_graph(graph_path)
    metadata: Dict[str, Any] = load_metadata(xx, data_path)

    ### LOOP FOR THE SPECIFIED NUMBER OF CONFORMING CANDIDATES ###

    lowest_energy: float = float("inf")
    scores: List[Dict] = list()
    candidates: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    conforming_count: int = 0
    seed: int = start

    with open(root_log, "a") as f:
        for i, seed in enumerate(range(start, start + iterations)):
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
                    verbose=verbose,
                )
                complete(
                    dccvt_consolidated,
                    dccvt_adjacencies,
                    dccvt_points,
                    dccvt_complete,
                    verbose=verbose,
                )

                # De-index Balzer assignments to use GEOIDs.
                postprocess(dccvt_complete, points_csv, dccvt_output, verbose=verbose)

                # Calculate the energy & population deviation of the map.
                energy: float = calc_energy_file(dccvt_complete, dccvt_points)
                popdev: float = calc_population_deviation_file(
                    dccvt_output, populations, total_pop, N
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
                    shutil.copy(dccvt_output, root_map)

            except Exception as e:
                print(f"Failure: {e}", file=f)
                continue

        print(
            f"{conforming_count} conforming candidates took {seed - start + 1} random seeds.",
            file=f,
        )

    ### SAVE THE CANDIDATE MAPS & THEIR SCORES ###

    write_json(root_candidates, candidates)

    fields: List[str] = list(scores[0].keys())
    write_csv(root_scores, scores, fields, precision="{:.6f}")


def parse_args() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(
        description="Find an approximate root map for a state."
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
        "-u",
        "--unsimplified",
        dest="unsimplified",
        action="store_true",
        help="Use unsimplified points & adjacencies",
    )
    parser.add_argument(
        "-q",
        "--qualify",
        dest="qualify",
        action="store_true",
        help="Qualify the outputs",
    )

    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
    )

    args: Namespace = parser.parse_args()
    return args


if __name__ == "__main__":
    main()

### END ###
