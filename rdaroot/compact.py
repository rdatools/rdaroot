"""
MINIMIZE ENERGIES / MAXIMIZE POPULATION COMPACTNESS OF AN ENSEMBLE
"""

from typing import Any, Dict, List, Tuple

from rdabase import (
    mkPoints,
    mkAdjacencies,
    populations,
    total_population,
    Graph,
    Point,
    Assignment,
    IndexedWeightedAssignment,
    index_geoids,
    index_assignments,
)
from rdascore import (
    load_plan,
)
from rdadccvt import (
    file_list,
    clean,
    dccvt_initial,
    dccvt_points,
    dccvt_adjacencies,
    dccvt_balzer2,
    dccvt_consolidated,
    dccvt_complete,
    dccvt_output,
    index_points_file,
    index_pairs_file,
    balzer_go,
    consolidate,
    postprocess,
    calc_energy_file,
    calc_population_deviation_file,
    write_redistricting_points,
    write_assignments,
)


def minimize_energies(
    plans: List[Dict[str, str | float | Dict[str, int | str]]],
    data: Dict[str, Dict[str, int | str]],
    shapes: Dict[str, Any],
    graph: Dict[str, List[str]],
    metadata: Dict[str, Any],
    logfile,
    *,
    roughly_equal: float = 0.02,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Minimize the energies / maximize the population compactness of an ensemble of maps."""

    points: List[Point] = mkPoints(data, shapes)
    pairs: List[Tuple[str, str]] = mkAdjacencies(Graph(graph))

    temp_points: str = "temp/NC_2020_points.csv"
    write_redistricting_points(points, temp_points)

    index_points_file(points, dccvt_points)
    index_pairs_file(points, pairs, dccvt_adjacencies)
    indexed_geoids: Dict[str, int] = index_geoids(points)

    pop_by_geoid: Dict[str, int] = populations(data)
    total_pop: int = total_population(pop_by_geoid)

    min_energy_ensemble: Dict[str, Any] = dict()
    min_energy_plans: List[Dict[str, str | float | Dict[str, int | str]]] = list()

    N: int = int(metadata["D"])

    count: int = 0
    lowest_plan: str = ""
    lowest_energy: float = float("inf")

    for i, p in enumerate(plans):
        print(f"... {i} ...")
        print(f"... {i} ...", file=logfile)

        clean(file_list)

        plan_name: str = str(p["name"])
        plan_dict: Dict[str, int | str] = p["plan"]  # type: ignore
        assignments: List[Assignment] = [
            Assignment(geoid, district) for geoid, district in plan_dict.items()
        ]
        indexed_assignments: List[IndexedWeightedAssignment] = index_assignments(
            assignments, indexed_geoids, pop_by_geoid
        )
        write_assignments(dccvt_initial, indexed_assignments)

        try:
            balzer_go(
                dccvt_points,
                dccvt_adjacencies,
                dccvt_initial,
                dccvt_balzer2,
                balance=True,
            )
            consolidate(
                dccvt_balzer2,
                dccvt_adjacencies,
                plan_name,
                dccvt_consolidated,
                verbose=verbose,
            )
            postprocess(
                dccvt_consolidated,
                temp_points,
                dccvt_output,
                verbose=verbose,
            )

        except Exception as e:
            print(f"Failure: {e}", file=logfile)
            continue

        assignments: List[Assignment] = load_plan(dccvt_output)
        plan: Dict[str, int | str] = {a.geoid: a.district for a in assignments}
        min_energy_plans.append({"name": plan_name, "plan": plan})  # No weights.
        count += 1

        energy: float = calc_energy_file(dccvt_consolidated, dccvt_points)
        popdev: float = calc_population_deviation_file(
            dccvt_output, pop_by_geoid, total_pop, N
        )

        if popdev < roughly_equal and energy < lowest_energy:
            lowest_energy = energy
            lowest_plan = plan_name

    min_energy_ensemble["size"] = count
    min_energy_ensemble["lowest_plan"] = lowest_plan
    min_energy_ensemble["lowest_energy"] = lowest_energy
    min_energy_ensemble["plans"] = min_energy_plans

    return min_energy_ensemble


### END ###
