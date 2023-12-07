# rdaroot

Root redistricting maps (plans)

## Definition

The root map for a state is the redistricing plan that has the greatest total population 
of its common core districts with respect to other valid maps, where
total population includes people of all ages for a precinct (VTD) and
the common core districts of two maps are the subsets of precinct assignments 
that yield the most shared population between corresponding districts of the two maps.
In other words, the root map has the lowest overall edit distance from all other valid maps, 
where the edit distance between two maps is the population of the precincts 
that must be reassigned to transform one map into the other. 

As identifying the ultimate root districts for a state is computationally infeasible, 
one must use a heuristic to generate an *approximate* root map. 
Our heuristic is to maximize population compactness.
The fundamental principle of these maps is that people who live near each other 
tend to be in the same district. 
Moreover, as they have low overall edit distances to other valid maps 
they are a good heuristic for approximating root maps. 

Maps that are highly compact *geometrically* also tend to have low overall edit distances to other valid maps 
&#8212; slightly lower than population-compact maps. 
But as Chief Justice Earl Warren said in his landmark *Reynold v. Sims* decision:
"Legislators represent people, not trees or acres." 
so we approximate root maps by maximizing population compactness.

Roughly speaking, population-compact districts form a 
[Voronoi diagram](https://en.wikipedia.org/wiki/Voronoi_diagram).

## Method

Elliding I/O details, this is how the heuristic search works:

-   We generate a random contiguous map with districts that have 'roughly equal' populations,
    using spanning trees.
-   We use those initial precinct-to-district assignments as a starting point for the next step.
-   We run Balzer\'s 
    [Capacity-Constrained Voronoi Tessellations: Computation and Applications](http://nbn-resolving.de/urn:nbn:de:bsz:352-opus-84645) 
    algorithm to find the lowest energy set of assignments given the initial assignments.
    In this process, we keep districts contiguous with 'roughly equal' populations, 
    a domain-specific modification of Balzer.
    In physics terms, these districts can be thought of as minimizing the moment of inertia or energy; 
    in the redistricting context, as maximizing population compactness. 
-   The Balzer algorithm may split some precincts across districts,
    so next we un-split these precincts so each precinct is assigned to one and only one district.
    We try to keep districts as balanced as possible in this process.
-   If the resulting map has a population deviation of less than 2%,
    it is considered a conforming candidate.
    Otherwise, we discard it.

We do the above for 100 conforming candidate maps and pick the lowest energy plan.
That is our approximate root map.

## Installation

Clone the repository:

```bash
$ git clone https://github.com/alecramsay/rdaroot
$ cd rdaroot
```

There is no package to install, just command line scripts to run.
However, you probably want to also clone the [rdabase](https://github.com/alecramsay/rdabase) repository.

## Usage

First convert precinct population, shape, and adjacency data into the formats expected by the Balzer code.
The scripts shown below draw data from `rdabase`.
Then run the script to heuristically search for an approximate root map.

```bash
scripts/make_points_file.py -d ../rdabase/data/NC/NC_2020_data.csv -s ../rdabase/data/NC/NC_2020_shapes_simplified.json -p temp/NC_2020_points.csv
scripts/make_adjacent_pairs.py -g ../rdabase/data/NC/NC_2020_graph.json -p temp/NC_2020_adjacencies.csv
scripts/approx_root.py -s NC -p temp/NC_2020_points.csv -a temp/NC_2020_adjacencies.csv
```

The `-s NC` flag indicates the state, North Carolina in this example.
The `-i-` flag (not shown) specifies the number of iterations to run. The default is 100.

The resulting map will be in the `maps` directory with a name of the form `NC_2020_root_100.csv`,
where `2020` is the census cycle and `100` is the number of iterations.
This precinct-assignment file can be imported into [Dave's Redistricting](https://davesredistricting.org/) (DRA).

## Testing

There are no automated tests. To test the script, run it on the example data:
