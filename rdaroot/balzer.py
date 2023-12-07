"""
BALZER ALGORITHM, I/O WRAPPERS, PRE & POST-PROCESSING

Copied from proebsting/dccvt.

- I added the wrappers.
- I wrapped the individual functions in try/except blocks.
- I tweaked a few other things noted below.

"""

import os
import random
from collections import defaultdict, Counter
import heapq

from typing import Any, List, Dict, Tuple, Set, Optional, DefaultDict, NamedTuple

import rdadata as rdadata
from rdafn import load_plan

from .union_find import StrUnionFind, IntUnionFind
from .balzerio import (
    LatLong,
    Point,
    Assignment,
    Redistricting_Point,
    Redistricting_Assignment,
    # get_GEOID,
    # get_DISTRICT,
    read_redistricting_points,
    # read_redistricting_pairs,
    write_latlongs,
    read_latlongs,
    read_points,
    write_points,
    # read_redistricting_assignment,
    write_redistricting_assignment,
    read_assignments,
    write_assignments,
    read_adjacencies,
    write_adjacent_pairs,
)


### PRE-BALZER INPUT CONVERSIONS ###


def index_points_file(
    points: List[Redistricting_Point],
    output: str,
    epsilon: float = 0.01,
    *,
    verbose: bool = False,
):
    """MODIFIED to take points already read in."""

    # TODO - Rationalize this
    raw_points: List[Dict[str, Any]] = [
        {"GEOID": p.geoid, "POP": p.pop, "X": p.ll.lat, "Y": p.ll.long} for p in points
    ]
    ps: List[Point] = rdadata.index_points(raw_points, epsilon)

    write_points(ps, output)


# TODO - DELETE
# def index_points_file(
#     points: List[Redistricting_Point],
#     output: str,
#     epsilon: float = 0.01,
#     *,
#     verbose: bool = False,
# ):
#     """MODIFIED to take points already read in."""

#     ps: List[Point] = [Point(p.ll, max(epsilon, p.pop)) for p in points]

#     assert epsilon > 0 or sum(p.pop for p in ps) == sum(p.pop for p in points)

#     write_points(ps, output)


# Accept
def index_pairs_file(
    points: List[Redistricting_Point],
    pairs: List[Tuple[str, str]],
    output: str,
    *,
    verbose: bool = False,
):
    """MODIFIED to take points & pairs already read in."""

    # TODO - Rationalize this
    raw_points: List[Dict[str, Any]] = [
        {"GEOID": p.geoid, "POP": p.pop, "X": p.ll.lat, "Y": p.ll.long} for p in points
    ]
    offset_by_geoid: Dict[str, int] = {p.geoid: i for i, p in enumerate(points)}
    adjacent_pairs: List[Tuple[int, int]] = rdadata.index_pairs(offset_by_geoid, pairs)

    write_adjacent_pairs(output, adjacent_pairs)


# TODO - DELETE
# def index_pairs_file(
#     points: List[Redistricting_Point],
#     pairs: List[Tuple[str, str]],
#     output: str,
#     *,
#     verbose: bool = False,
# ):
#     """MODIFIED to take points & pairs already read in."""

#     mapping: Dict[str, int] = {p.geoid: i for i, p in enumerate(points)}
#     pairs = [
#         (p1, p2) for p1, p2 in pairs if p1 != "OUT_OF_STATE" and p2 != "OUT_OF_STATE"
#     ]
#     adjacent_pairs: List[Tuple[int, int]] = [
#         (mapping[p1], mapping[p2]) for p1, p2 in pairs
#     ]

#     geoids: Set[str] = set(p.geoid for p in points)
#     report_disconnect(pairs, geoids, "all points", verbose)
#     write_adjacent_pairs(output, adjacent_pairs)


def index_assignments_file(
    assignname: str,
    offset_by_geoid: Dict[str, int],
    pop_by_geoid: Dict[str, int],
    output: str,
    *,
    verbose: bool = False,
):
    """ADDED: Index the initial assignments

    - mapping is the mapping from GEOID to index offset.
    - pop_by_geoid is the mapping from GEOID to population.

    """

    # TODO - Rationalize this
    # redistricting_assignments: List[
    #     Redistricting_Assignment
    # ] = read_redistricting_assignment(assignname)
    plan: List[Dict[str, str | int]] = load_plan(assignname)

    assigns: List[Assignment] = rdadata.index_assignments(
        plan, offset_by_geoid, pop_by_geoid
    )

    write_assignments(output, assigns)


# TODO - DELETE
# def index_assignments_file(
#     assignname: str,
#     mapping: Dict[str, int],
#     pop_by_geoid: Dict[str, int],
#     output: str,
#     *,
#     verbose: bool = False,
# ):
#     """ADDED: Index the initial assignments

#     - mapping is the mapping from GEOID to index offset.
#     - pop_by_geoid is the mapping from GEOID to population.

#     """

#     redistricting_assignments: List[
#         Redistricting_Assignment
#     ] = read_redistricting_assignment(assignname)

#     assigns: List[Assignment] = list()
#     for p in redistricting_assignments:
#         indexed: Assignment = Assignment(
#             site=int(p.district) - 1,  # Assume 1-N districts for simplicity
#             point=mapping[p.geoid],
#             pop=float(pop_by_geoid[p.geoid]),
#         )
#         assigns.append(indexed)

#     write_assignments(output, assigns)


def randomsites(input: str, output: str, N: int, seed: int):
    random.seed(seed)
    points: List[Point] = read_points(input)
    sample: List[Point] = random.sample(list(set(points)), N)  # set to avoid duplicates
    sites: List[LatLong] = [p.ll for p in sample]
    write_latlongs(sites, output)


def initial(sitename: str, pointname: str, output: str):
    sites: List[LatLong] = read_latlongs(sitename)
    points: List[Point] = read_points(pointname)
    assigns: List[Assignment] = get_initial(sites, points)

    start: List[float] = [p.pop for p in points]
    for a in assigns:
        start[a.point] -= a.pop
    assert all(abs(s) < 0.0001 for s in start)

    write_assignments(output, assigns)


def mk_contiguous(assignname: str, adjacentname: str, output: str) -> None:
    assignments: List[Assignment] = read_assignments(assignname)
    adjacents = read_adjacencies(adjacentname)

    check_connected(assignments, adjacents)
    contig: List[Assignment] = get_contiguous(assignments, adjacents)
    check_connected(contig, adjacents)

    start: DefaultDict[int, float] = defaultdict(float)
    for a in assignments:
        start[a.point] += a.pop
    for a in contig:
        start[a.point] -= a.pop
    assert all(abs(s) < 0.0001 for s in start.values())
    write_assignments(output, contig)


### BALZER ALGORITHM PROPER (in Go) ###


def balzer_go(
    points: str, adjacencies: Optional[str], initial: str, output: str, balance: bool
) -> None:
    """Run Balzer's algorithm (DCCVT) to find a maximally population compact map."""

    exe_path: str = "bin/dccvt"  # Local copy of the executable
    adjacencies_flag: str = f"--adjacencies {adjacencies}" if adjacencies else ""
    balance_num: int = 10
    balance_flag: str = f"--balance {balance_num}" if balance else ""
    threshold: int = 1000

    command: str = f"{exe_path} --points {points} {adjacencies_flag} --initial {initial} --threshold {threshold} --output {output} {balance_flag}"
    os.system(command)

    if not os.path.exists(output):
        raise Exception(f"Balzer's algorithm failed to produce an output file.")


### POST-BALZER PROCESSING ###


def consolidate(
    assignname: str,
    adjacentname: str,
    label: str,
    output: str,
    *,
    verbose: bool = False,
) -> None:
    assignments: List[Assignment] = read_assignments(assignname)
    adjacents = read_adjacencies(adjacentname)
    consolidated: List[Assignment] = get_consolidated(
        assignments, adjacents, label, verbose
    )
    start: DefaultDict[int, float] = defaultdict(float)

    for a in assignments:
        start[a.point] += a.pop
    for a in consolidated:
        start[a.point] -= a.pop
    assert all(abs(s) < 0.0001 for s in start.values())
    totals: Dict[int, float] = defaultdict(float)
    for a in consolidated:
        totals[a.site] += a.pop
    maximum = int(max(totals.values()))
    minimum = int(min(totals.values()))
    average = sum(totals.values()) / len(totals)

    if verbose:
        print(
            f"Map {label} = {minimum} to {maximum}, Diff = {maximum - minimum}, Percent = {100 * (maximum - minimum) / average:.3f}%"
        )

    write_assignments(output, consolidated)


def complete(
    assignname: str,
    adjacentname: str,
    pointsname: str,
    output: str,
    *,
    verbose: bool = False,
) -> None:
    assignments: List[Assignment] = read_assignments(assignname)
    adjacents = read_adjacencies(adjacentname)
    points = read_points(pointsname)

    assigns: List[Assignment] = get_complete(assignments, adjacents, points, verbose)
    write_assignments(output, assigns)


def postprocess(
    input: str,
    redistricting_input: str,
    output: str,
    *,
    verbose: bool = False,
) -> None:
    assignments: List[Assignment] = read_assignments(input)
    redistricting_points: List[Redistricting_Point] = read_redistricting_points(
        redistricting_input
    )
    redistricting_assignments: List[
        Redistricting_Assignment
    ] = get_redistricting_assignments(assignments, redistricting_points)

    inpoints: Set[int] = set(a.point for a in assignments)
    outpoints: Set[str] = set(a.geoid for a in redistricting_assignments)
    assert len(inpoints) == len(outpoints)
    write_redistricting_assignment(output, redistricting_assignments)


### HELPERS ###


def report_disconnect(
    pairs: List[Tuple[str, str]], geoids: Set[str], msg: str, verbose: bool = False
):
    ds = StrUnionFind(geoids)
    for p1, p2 in pairs:
        if (
            p1 != "OUT_OF_STATE"
            and p2 != "OUT_OF_STATE"
            and p1 in geoids
            and p2 in geoids
        ):
            ds.merge(p1, p2)
    if ds.n_subsets > 1:
        subset: Set[str] = min(ds.subsets(), key=len)
        if len(subset) > 10:
            summary = f"{list(subset)[:10]}..."
        else:
            summary = f"{list(subset)}"
        if verbose:
            print(
                f"WARNING: {ds.n_subsets} disconnected {msg} regions, including: {summary}"
            )


def get_initial(sites: List[LatLong], points: List[Point]) -> List[Assignment]:
    class Unflattened_Assignment(NamedTuple):
        site: LatLong
        point_index: int
        pop: float

    total: float = sum([p.pop for p in points])
    ave: float = total / len(sites)
    pop_per_site: DefaultDict[LatLong, float] = defaultdict(float)  # site -> pop
    pop_per_point: DefaultDict[int, float] = defaultdict(float)  # point -> pop
    initial: List[Unflattened_Assignment] = []
    h: List[Tuple[float, int, LatLong]] = []
    for index, p in enumerate(points):
        for s in sites:
            d = (p.ll.lat - s.lat) ** 2 + (p.ll.long - s.long) ** 2
            heapq.heappush(h, (d, index, s))
    while len(h) > 0:
        d: float
        index: int
        s: LatLong
        d, index, s = heapq.heappop(h)
        p: Point = points[index]
        point_remaining: float = p.pop - pop_per_point[index]
        if point_remaining <= 0:
            continue
        site_remaining: float = ave - pop_per_site[s]
        if site_remaining <= 0:
            continue
        pop = min(point_remaining, site_remaining)
        pop_per_site[s] += pop
        pop_per_point[index] += pop
        initial.append(Unflattened_Assignment(s, index, pop))
    initial_sum: float = sum([i.pop for i in initial])
    assert abs(initial_sum - total) < 0.0001, f"{initial_sum} != {total}"
    s2n: Dict[LatLong, int] = {s: i for i, s in enumerate(sites)}
    assigns: List[Assignment] = [
        Assignment(s2n[s], index, pop) for s, index, pop in initial
    ]
    return assigns


def check_connected(
    assignments: List[Assignment], adjacents: List[Tuple[int, int]]
) -> None:
    points: Set[int] = {a.point for a in assignments} | {
        p for p1, p2 in adjacents for p in (p1, p2)
    }
    ds = IntUnionFind(points)
    for p1, p2 in adjacents:
        ds.merge(p1, p2)
    if ds.n_subsets > 1:
        print(
            f"WARNING: not all points are connected in adjacents: {ds.n_subsets-1} disconnected set(s):"
        )
        subsets: List[Set[int]] = sorted(list(ds.subsets()), key=lambda s: len(s))
        for s in subsets[:-1]:
            print(f"  disconnected: {s}")


def get_contiguous(
    assignments: List[Assignment], adjacents: List[Tuple[int, int]]
) -> List[Assignment]:
    num_sites = max(a.site for a in assignments) + 1
    clusters = count_clusters(assignments, adjacents, True)
    if clusters != count_clusters(assignments, adjacents, False):
        print("WARNING: significant shared points in assignments")
    if clusters == num_sites:
        return assignments

    assert all(a.pop > 0 for a in assignments)
    allpoints = {a.point for a in assignments}
    neighbors: DefaultDict[int, Set[int]] = defaultdict(set)
    for p1, p2 in adjacents:
        if p1 in allpoints and p2 in allpoints:
            neighbors[p1].add(p2)
            neighbors[p2].add(p1)

    assigned: Dict[int, Set[int]] = defaultdict(set)
    for a in assignments:
        assigned[a.point].add(a.site)

    ds = IntUnionFind(allpoints)
    for p1, p2 in adjacents:
        if assigned[p1] == assigned[p2] and len(assigned[p1]) == 1:
            ds.merge(p1, p2)

    while ds.n_subsets > num_sites:
        subsets: List[Set[int]] = ds.subsets()
        smallest = min(subsets, key=lambda s: len(s))
        counter: Dict[int, int] = Counter()
        for p in smallest:
            for n in neighbors[p]:
                if not ds.connected(p, n):
                    counter[ds[n]] += 1
        assert len(counter) > 0, f"no neighboring blocks for {smallest}"
        biggest: int = max(counter.items(), key=lambda x: x[1])[0]
        for p in smallest:
            ds.merge(p, biggest)
            break
    root2site: Dict[int, int] = {}
    p: int
    for p in ds.__iter__():
        root: int = ds[p]
        if root not in root2site:
            root2site[root] = len(root2site)
    assigns = [Assignment(root2site[ds[a.point]], a.point, a.pop) for a in assignments]
    return assigns


def mindiff(
    allocations: List[Assignment],
    adjacents: List[Tuple[int, int]],
    verbose: bool = False,
) -> List[Assignment]:
    numsites = max(a.site for a in allocations) + 1
    totals: DefaultDict[int, float] = defaultdict(float)
    total: float = 0.0
    for a in allocations:
        totals[a.site] += a.pop
        total += a.pop
    ave: float = total / len(totals)

    p2s2amount: Dict[int, Dict[int, float]] = {}
    for a in allocations:
        if a.point not in p2s2amount:
            p2s2amount[a.point] = defaultdict(float)
        p2s2amount[a.point][a.site] += a.pop
    remove = [
        (p, s) for p in p2s2amount for s in p2s2amount[p] if p2s2amount[p][s] == 0.0
    ]
    for x, y in remove:
        del p2s2amount[x][y]
    assigned: Dict[int, List[Assignment]] = {}
    for p in p2s2amount:
        if len(p2s2amount[p]) > 1:
            assigned[p] = [Assignment(s, p, p2s2amount[p][s]) for s in p2s2amount[p]]
    multiple: List[Tuple[int, List[Assignment]]] = list(assigned.items())

    byrisk: List[Tuple[int, List[Assignment]]] = sorted(
        multiple, key=lambda p: max(pop.pop for pop in p[1]), reverse=True
    )
    adjustments: List[Assignment] = []
    for _, allocs in byrisk:
        subtotal: float = sum(a.pop for a in allocs)
        candidates: List[List[Assignment]] = [
            [
                Assignment(a.site, a.point, -a.pop if i != j else subtotal - a.pop)
                for j, a in enumerate(allocs)
            ]
            for i in range(len(allocs))
        ]
        bests: List[List[Assignment]] = sorted(
            candidates,
            key=lambda c: max(abs(totals[a.site] + a.pop - ave) for a in c),
        )
        found = False
        for best in bests:
            c = count_clusters(allocations + adjustments + best, adjacents)
            if c == numsites:
                found = True
                adjustments.extend(best)
                for a in best:
                    totals[a.site] += a.pop
                break
        if not found:
            raise Exception(f"Could not find a way to make consolidated map contiguous")

    return adjustments


def count_site_clusters(
    site: int,
    assignments: List[Assignment],
    adjacents: List[Tuple[int, int]],
    shared: bool = True,
) -> int:
    accumulate: Dict[int, float] = defaultdict(float)
    others: Dict[int, float] = defaultdict(float)
    for a in assignments:
        if a.site == site:
            accumulate[a.point] += a.pop
        else:
            others[a.point] += a.pop
    points: Set[int] = {
        p for p, v in accumulate.items() if v > 0 and (shared or others[p] == 0)
    }
    ds = IntUnionFind(points)
    for p1, p2 in adjacents:
        if p1 in points and p2 in points:
            ds.merge(p1, p2)
    return ds.n_subsets


def count_clusters(
    assignments: List[Assignment],
    adjacents: List[Tuple[int, int]],
    shared: bool = True,
) -> int:
    sites: set[int] = {a.site for a in assignments}
    count = 0
    for s in sites:
        count += count_site_clusters(s, assignments, adjacents, shared=shared)
    return count


def get_consolidated(
    assignments: List[Assignment],
    adjacents: List[Tuple[int, int]],
    label: str,
    verbose: bool = False,
) -> List[Assignment]:
    clusters: int = count_clusters(assignments, adjacents)
    adjustments: List[Assignment] = mindiff(assignments, adjacents, verbose)
    clusters2 = count_clusters(assignments + adjustments, adjacents)
    if clusters != clusters2:
        if verbose:
            # print(
            #     f"WARNING: Map {label} = {clusters} != {clusters2}"
            # )
            raise Exception(f"WARNING: Map {label} = {clusters} != {clusters2}")
    p2s: Dict[int, Dict[int, float]] = {}
    for a in assignments + adjustments:
        if a.point not in p2s:
            p2s[a.point] = defaultdict(float)
        p2s[a.point][a.site] += a.pop

    consolidated: List[Assignment] = []
    for p in p2s:
        site = max(p2s[p].items(), key=lambda x: x[1])[0]
        consolidated.append(Assignment(site, p, p2s[p][site]))
    numsites: int = max(a.site for a in consolidated) + 1
    clusters3 = count_clusters(consolidated, adjacents)
    if numsites == clusters3:
        if verbose:
            print(f"Map {label} = Contiguous {clusters3}")
    else:
        if verbose:
            print(
                f"Map {label} = Discontiguous {clusters3} != {numsites}"
            )  # TODO -- Raise an exception? <<< Todd
    return consolidated


def get_complete(
    assigns: List[Assignment],
    adjacents: List[Tuple[int, int]],
    points: List[Point],
    verbose: bool = False,
) -> List[Assignment]:
    p2s: Dict[int, int] = {}
    for a in assigns:
        assert a.point not in p2s
        p2s[a.point] = a.site
    adj: Dict[int, Set[int]] = defaultdict(set)
    for p1, p2 in adjacents:
        adj[p1].add(p2)
        adj[p2].add(p1)
    additional: List[Assignment] = []
    for index, p in enumerate(points):
        if index not in p2s:
            assert p.pop == 0
            # assert len(adj[index]) > 0, index
            counter: Dict[int, int] = Counter()
            for n in adj[index]:
                if n in p2s:
                    counter[p2s[n]] += 1
            if len(counter) == 0:
                if verbose:
                    print("point has no neighbors:", index)
            else:
                p2s[index] = counter.most_common(1)[0][0]
                additional.append(Assignment(p2s[index], index, p.pop))
    return assigns + additional


def get_redistricting_assignments(
    assignments: List[Assignment],
    redistricting_points: List[Redistricting_Point],
) -> List[Redistricting_Assignment]:
    redistricting_dict: Dict[Redistricting_Point, int] = {}
    p: Redistricting_Point
    s: int
    for a in assignments:
        p = redistricting_points[a.point]
        s = a.site
        assert p not in redistricting_dict
        redistricting_dict[p] = s
    redistricting_assignments: List[Redistricting_Assignment] = []
    for p in redistricting_points:
        if p not in redistricting_dict:
            # should we do something here for unassigned points?
            assert p.pop == 0
            continue
        s = redistricting_dict[p]
        red_assgin = Redistricting_Assignment(p.geoid, s)
        redistricting_assignments.append(red_assgin)
    return redistricting_assignments


# TODO - DELETE
# def squared_distance(a: LatLong, b: LatLong) -> float:
#     return (a.lat - b.lat) * (a.lat - b.lat) + (a.long - b.long) * (a.long - b.long)


# def get_centroids(assigns: List[Assignment], points: List[Point]) -> List[LatLong]:
#     bysite: DefaultDict[int, List[Assignment]] = defaultdict(list)
#     for a in assigns:
#         bysite[a.site].append(a)
#     cs: List[LatLong] = []
#     top: int = max(s for s in bysite.keys())
#     for site in range(top + 1):
#         persite: List[Assignment] = bysite[site]
#         total: float = sum(a.pop for a in persite)
#         lat: float = sum(points[a.point].ll.lat * a.pop for a in persite) / total
#         long: float = sum(points[a.point].ll.long * a.pop for a in persite) / total
#         cs.append(LatLong(lat, long))
#     return cs


def calc_energy(assignname: str, pointname: str) -> float:
    """Calculate the energy of a map."""

    assignments: List[Assignment] = read_assignments(assignname)
    points: List[Point] = read_points(pointname)
    energy: float = rdadata.calc_energy(assignments, points)

    return energy


# TODO - DELETE
# def calc_energy(assignname: str, pointname: str) -> float:
#     """Calculate the energy of a map.

#     MODIFIED to return the energy, rather than print it.
#     """

#     assignments: List[Assignment] = read_assignments(assignname)
#     points: List[Point] = read_points(pointname)
#     sites: List[LatLong] = get_centroids(assignments, points)
#     total: float = sum(
#         a.pop
#         * squared_distance(
#             sites[a.site], points[a.point].ll
#         )  # not sqrt!!! moment of inertia!
#         for a in assignments
#     )

#     return total


def calc_population_deviation(
    assignname: str, pop_by_geoid: Dict[str, int], total_pop: int, n_districts: int
) -> float:
    """Calculate the population deviation of a map."""

    plan: List[Dict[str, str | int]] = load_plan(assignname)
    deviation: float = rdadata.calc_population_deviation(
        plan, pop_by_geoid, total_pop, n_districts
    )

    return deviation


# TODO - DELETE
# def calc_population_deviation(
#     assignname: str, pop_by_geoid: Dict[str, int], total_pop: int, n_districts: int
# ) -> float:
#     """ADDED: Calculate the population deviation of a map."""

#     redistricting_assignments: List[
#         Redistricting_Assignment
#     ] = read_redistricting_assignment(assignname)

#     pop_by_district: DefaultDict[int | str, int] = defaultdict(int)

#     for p in redistricting_assignments:
#         pop_by_district[p.district] += pop_by_geoid[p.geoid]

#     max_pop: int = max(pop_by_district.values())
#     min_pop: int = min(pop_by_district.values())
#     target_pop: int = int(total_pop / n_districts)

#     deviation: float = rda.calc_population_deviation(max_pop, min_pop, target_pop)

#     return deviation


### END ###
