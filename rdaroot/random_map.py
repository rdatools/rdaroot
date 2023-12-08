"""
RANDOM MAP
Generate a random map with N contiguous, 'roughly equal' population districts.

This code is adapted from Todd Proebsting's early work in the `ensembles` project.
He wrote most of the code which I only lightly edited to make it work in this context.
"""

import random

from typing import List, Dict, Tuple, Set, Optional

from .balzerio import Assignment, write_redistricting_assignments


def random_map(
    adjacencies: List[Tuple[str, str]],
    populations: Dict[str, int],
    N: int,
    seed: int,
    # initial_csv: str,
    *,
    roughly_equal: float = 0.01,
    attempts_per_seed: int = 1000,
    # verbose: bool = False,
) -> List[Assignment]:
    """Generate a random map with N contiguous, 'roughly equal' population districts."""

    random.seed(seed)

    total_population: int = sum(populations.values())
    target_population: int = int(total_population / N)
    root: Node

    while True:
        tbc: Set[str] = set(populations.keys())
        district: int = 1
        assignments: Dict[str, int] = {}
        tree_pops: Dict[str, int]
        counter: int = 0
        while True:
            counter += 1
            if counter > attempts_per_seed:
                raise Exception(f"Too many attempts for seed ({seed})")
                # The random seed is updated after each call,
                # so the process should eventually succeed.

            # Calculate the population yet to be assigned.
            remaining_population = sum(populations[geoid] for geoid in tbc)
            if remaining_population < target_population * 1.5:  # hack
                break

            # Get a spanning tree.
            root = Create(tbc, adjacencies, populations)
            tree_pops = tree_populations(root, populations)
            all_nodes: List[Node] = nodes_in_tree(root)

            # Sort the cuts by their deviation from the target population, and
            # then filter out the ones that wouldn't yield 'roughly equal' population.
            ranked = sorted(
                all_nodes,
                key=lambda n: abs(tree_pops[n.id] - target_population)
                / target_population,
            )
            ranked = [
                n
                for n in ranked
                if abs(tree_pops[n.id] - target_population) / target_population
                < roughly_equal
            ]
            if not ranked:
                continue

            # Choose one of the candidate cuts at random.
            random_i = random.randint(0, 20)
            if random_i >= len(ranked):
                continue
            choice: Node = ranked[random_i]

            # If the deviation of the district would be too large, try again.
            deviation = (
                abs(tree_pops[choice.id] - target_population) / target_population
            )
            if deviation > roughly_equal:
                continue

            # If the deviation of the remaining population would be too large, try again.
            deviation = (
                abs(
                    (remaining_population - tree_pops[choice.id]) / (N - district)
                    - target_population
                )
                / target_population
            )
            if deviation > roughly_equal:
                continue

            # Assign the GEOIDs in the chosen cut to the current district.
            assign_district(choice, district, tbc, assignments)

            # Increment the district and repeat.
            district += 1

        # Must handle the last district, which may have a bad size.
        assert (
            abs(remaining_population - target_population)
        ) / target_population < roughly_equal
        root = Create(tbc, adjacencies, populations)
        assign_district(root, district, tbc, assignments)
        break

    # note that this may not generate N districts due to spanning tree issues.
    n_assigned: int = len(set(assignments.values()))
    if n_assigned != N:
        raise Exception(
            f"Failed to generate {N} districts. Only generated {len(assignments.values())}."
        )

    # Convert the assignments (dict) into a plan.
    plan: List[Assignment] = [
        Assignment(geoid=geoid, district=district)  # districts 1-N
        for geoid, district in assignments.items()
    ]

    return plan


# TODO - Required suporting code to be replaced.


class Node:
    id: str
    Next: Optional["Node"]
    InTree: bool
    neighbors: List["Node"]
    spanning_kids: List["Node"]

    def __init__(self, id: str, population: int):
        self.id = id
        self.Next = None
        self.InTree = False
        self.neighbors = []
        self.spanning_kids = []

    def __repr__(self):
        return f"Node(id={self.id}, neighbors={len(self.neighbors)}, spanning_kids={len(self.spanning_kids)})"


# Generating Random Spanning Trees More Quickly than the Cover Time
# David Bruce Wilson
# https://www.cs.cmu.edu/~15859n/RelatedWork/RandomTrees-Wilson.pdf
def RandomTreeRoot(units: List[Node], r: Node):
    u: Optional[Node]
    for u in units:
        u.InTree = False
    r.InTree = True
    r.Next = None
    for i in units:
        assert i is not None
        u = i
        while not u.InTree:
            # NOTE - This should be using the same random seed set in random_map().
            u.Next = random.choice(u.neighbors)
            u = u.Next
            assert u is not None
        u = i
        while not u.InTree:
            u.InTree = True
            assert u.Next is not None
            u = u.Next
            assert u is not None


def Create(
    tbc: Set[str],
    adjacencies: List[tuple[str, str]],
    populations: Dict[str, int],
) -> Node:
    all = mklists(tbc, adjacencies, populations)
    root: Node = random.choice(all)
    RandomTreeRoot(all, root)
    n: Node
    for n in all:
        if n.Next is not None and n not in n.Next.spanning_kids:
            n.Next.spanning_kids.append(n)
    return root


def mklists(
    tbc: Set[str],
    adjacencies: List[tuple[str, str]],
    populations: Dict[str, int],
) -> List[Node]:
    nodes: Dict[str, Node] = {}
    for a in adjacencies:
        if a[0] in tbc and a[0] not in nodes:
            nodes[a[0]] = Node(a[0], populations[a[0]])
        if a[1] in tbc and a[1] not in nodes:
            nodes[a[1]] = Node(a[1], populations[a[1]])
        if a[0] in tbc and a[1] in tbc:
            nodes[a[0]].neighbors.append(nodes[a[1]])
            nodes[a[1]].neighbors.append(nodes[a[0]])
    all = list(nodes.values())
    return all


def nodes_in_tree(root: Node) -> List[Node]:
    nodes: List[Node] = []
    nodes.append(root)
    for n in root.spanning_kids:
        nodes.extend(nodes_in_tree(n))
    return nodes


#


def tree_populations0(
    root: Node, populations: Dict[str, int], tree_pops: Dict[str, int]
):
    tree_pops[root.id] = populations[root.id]
    for n in root.spanning_kids:
        tree_populations0(n, populations, tree_pops)
        tree_pops[root.id] += tree_pops[n.id]


def tree_populations(root: Node, populations: Dict[str, int]) -> Dict[str, int]:
    tree_pops: Dict[str, int] = {}
    tree_populations0(root, populations, tree_pops)
    return tree_pops


def assign_district(
    root: Node, district: int, tbc: Set[str], assignments: Dict[str, int]
):
    assert root.id not in assignments
    assignments[root.id] = district
    tbc.remove(root.id)
    for n in root.spanning_kids:
        assign_district(n, district, tbc, assignments)


### END ###
