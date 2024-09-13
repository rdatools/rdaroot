"""
MINIMIZE ENERGIES / MAXIMIZE POPULATION COMPACTNESS OF AN ENSEMBLE
"""

from typing import Any, Dict, List, Tuple, Set

from collections import defaultdict

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
    load_plan,
    is_connected,
)
from rdadccvt import (
    file_list,
    clean,
    dccvt_initial,
    dccvt_points,
    dccvt_adjacencies,
    dccvt_balzer2,
    dccvt_points_temp,
    dccvt_consolidated,
    # dccvt_complete,
    dccvt_output,
    index_points_file,
    index_pairs_file,
    balzer_go,
    consolidate,
    postprocess,
    calc_energy_file,
    calc_population_deviation_file,
    write_redistricting_points,
    read_assignments,
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
    debug: bool = False,
) -> Dict[str, Any]:
    """Minimize the energies / maximize the population compactness of an ensemble of maps."""

    working_files: List[str] = file_list
    working_files.remove(dccvt_points_temp)

    points: List[Point] = mkPoints(data, shapes)
    pairs: List[Tuple[str, str]] = mkAdjacencies(Graph(graph))

    write_redistricting_points(points, dccvt_points_temp)

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

        clean(working_files)

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

            ### DEBUG - VERIFY THAT THE BALERIZED PLAN IS STILL WELL FORMED
            if debug:
                well_formed: bool = True
                balzer_assignments: List[IndexedWeightedAssignment] = read_assignments(
                    dccvt_balzer2
                )

                # All points are assigned

                point_geoids: List[str] = [p.geoid for p in points]
                assignment_geoids: Set[str] = set(
                    [points[a.point].geoid for a in balzer_assignments]
                )
                for geoid in point_geoids:
                    if geoid not in assignment_geoids:
                        well_formed = False
                        print(
                            f"- Balzer did not assign {geoid} with population {data[geoid]['TOTAL_POP']}."
                        )
                if not well_formed:
                    print(f"Unpopulated geoids:")
                    for geoid in point_geoids:
                        if data[geoid]["TOTAL_POP"] == 0:
                            print(f"- {geoid}")
                    assert False

                # Districts are contiguous

                district_ids: List[Any] = []
                geoids_by_district: Dict[int | str, List[str]] = defaultdict(list)

                for a in balzer_assignments:
                    district_id: Any = a.site + 1
                    geoid: str = points[a.point].geoid

                    geoids_by_district[district_id].append(geoid)
                    if district_id not in district_ids:
                        district_ids.append(district_id)
                for district_id in district_ids:
                    geoids: List[str] = geoids_by_district[district_id]
                    if not is_connected(geoids, graph):
                        print(f"After Balzer, {p['name']} is not contiguous!")  # type: ignore
                        assert False

                print(f"Plan {p['name']}({i}) after Balzer is still well formed.")  # type: ignore
            ###

            consolidate(
                dccvt_balzer2,
                dccvt_adjacencies,
                plan_name,
                dccvt_consolidated,
                verbose=verbose,
            )

            postprocess(
                dccvt_consolidated,
                dccvt_points_temp,
                dccvt_output,
                verbose=verbose,
            )

        except Exception as e:
            print(f"Failure: {e}")
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
