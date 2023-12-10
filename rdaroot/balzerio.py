"""
BALZER READ/WRITE HELPERS

Copied from proebsting/dccvt.
Except the additions & modifications noted below, Todd Proebsting wrote this code.

"""

import csv

from typing import Any, Dict, List, Tuple

from rdabase import LatLong, Point, IndexedPoint, Assignment, IndexedWeightedAssignment


def get_GEOID(row: Dict[str, Any]) -> str:
    for k in row.keys():
        if k.startswith("GEOID"):
            return k
    raise ValueError(f"Could not find GEOID in {row}")


def get_DISTRICT(row: Dict[str, Any]) -> str:
    for k in row.keys():
        if k.upper().startswith("DISTRICT"):
            return k
    raise ValueError(f"Could not find DISTRICT in {row}")


#


def read_redistricting_points(input: str) -> List[Point]:
    # read GEOID, POP, X, Y from CSV
    red_points: List[Point] = []
    with open(input, "r") as f:
        reader = csv.DictReader(f)
        geoid = ""
        for row in reader:
            if not geoid:
                geoid = get_GEOID(row)
            red_point: Point = Point(
                geoid=row[geoid],
                pop=float(row["POP"]),
                ll=LatLong(
                    long=float(row["X"]),
                    lat=float(row["Y"]),
                ),
            )
            red_points.append(red_point)
    return red_points


def write_redistricting_points(points: List[Point], fname: str):
    with open(fname, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["GEOID", "POP", "X", "Y"])
        for point in points:
            row: List = [point.geoid, point.ll.lat, point.ll.long, point.pop]
            writer.writerow(row)


def read_redistricting_pairs(input: str) -> List[Tuple[str, str]]:
    # read GEOID1, GEOID2 from CSV
    red_pairs: List[Tuple[str, str]] = []
    with open(input, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            red_pair: Tuple[str, str] = (row[0], row[1])
            red_pairs.append(red_pair)
    return red_pairs


def write_latlongs(latlongs: List[LatLong], fname: str):
    with open(fname, "w") as f:
        writer = csv.writer(f)
        for latlong in latlongs:
            row: List[float] = [
                latlong.lat,
                latlong.long,
            ]  # should be lat/long?
            writer.writerow(row)


def read_latlongs(input: str) -> List[LatLong]:
    locations: List[LatLong] = []
    with open(input, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            ll: LatLong = LatLong(
                lat=float(row[0]),
                long=float(row[1]),
            )
            locations.append(ll)
    return locations


def read_points(input: str) -> List[IndexedPoint]:
    locations: List[IndexedPoint] = []
    with open(input, "r") as f:
        locations = []
        reader = csv.reader(f)
        for row in reader:
            pop: float = float(row[2]) if len(row) > 2 else 1.0
            point: IndexedPoint = IndexedPoint(
                ll=LatLong(lat=float(row[0]), long=float(row[1])),
                pop=pop,
            )
            locations.append(point)
    return locations


def write_points(points: List[IndexedPoint], fname: str):
    with open(fname, "w") as f:
        writer = csv.writer(f)
        for point in points:
            row: List[float] = [point.ll.lat, point.ll.long, point.pop]
            writer.writerow(row)


def read_redistricting_assignments(
    input: str,
) -> List[Assignment]:
    # read GEOID, DISTRICT from CSV
    red_assigns: List[Assignment] = []
    with open(input, "r") as f:
        reader = csv.DictReader(f)
        geoid = ""
        district = ""
        for row in reader:
            if not geoid:
                geoid = get_GEOID(row)
                district = get_DISTRICT(row)
            red_assign: Assignment = Assignment(
                geoid=row[geoid], district=int(row[district])
            )
            red_assigns.append(red_assign)
    return red_assigns


def write_redistricting_assignments(output: str, assigns: List[Assignment]):
    # write GEOID, DISTRICT to CSV
    with open(output, "w") as f:
        # write header
        writer = csv.writer(f)
        writer.writerow(["GEOID", "DISTRICT"])
        # write each row
        for a in assigns:
            district: str = (
                str(a.district + 1) if isinstance(a.district, int) else a.district
            )
            writer.writerow([a.geoid, district])


def read_assignments(input: str) -> List[IndexedWeightedAssignment]:
    # read site#, point#, pop from CSV
    allocations: List[IndexedWeightedAssignment] = []
    with open(input, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            allocation: IndexedWeightedAssignment = IndexedWeightedAssignment(
                site=int(row[0]),
                point=int(row[1]),
                pop=float(row[2]),
            )
            allocations.append(allocation)
    return allocations


def write_assignments(output: str, assigns: List[IndexedWeightedAssignment]):
    # write site#, point#, pop to CSV
    with open(output, "w") as f:
        writer = csv.writer(f)
        for a in assigns:
            writer.writerow([a.site, a.point, a.pop])


def read_adjacencies(input: str) -> List[Tuple[int, int]]:
    # read site#, site# from CSV
    pairs: List[Tuple[int, int]] = []
    with open(input, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            pairs.append((int(row[0]), int(row[1])))
    return pairs


def write_adjacent_pairs(input: str, pairs: List[Tuple[int, int]]):
    with open(input, "w") as f:
        writer = csv.writer(f)
        for p in pairs:
            writer.writerow(p)


### END ###
