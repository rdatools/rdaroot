# rdaroot

Root maps (redistricting plans)

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

-   We generate a collection of random contiguous map with districts that have 'roughly equal' populations.
-   We use those initial precinct-to-district assignments as the starting point for the next step.
-   For each input map, we run Balzer\'s 
    [Capacity-Constrained Voronoi Tessellations: Computation and Applications](http://nbn-resolving.de/urn:nbn:de:bsz:352-opus-84645) 
    algorithm
    to transform it into a map that minimizes the energy of the assignments.
    In this process, we keep districts contiguous with 'roughly equal' populations, 
    a domain-specific modification of Balzer.
    In physics terms, these districts can be thought of as minimizing the moment of inertia or energy; 
    in the redistricting context, they maximize population compactness. 
-   The Balzer algorithm may split some precincts across districts,
    so next we un-split these precincts so each is assigned to one and only one district.
    We try to keep districts as balanced as possible in this process.
-   If the resulting map has a population deviation of less than 2%,
    it is considered a conforming candidate.
    Otherwise, we ignore it.

Then we pick the lowest energy conforming candidate plan.
That is our approximate root map.

This process is agnostic to the method used to generate the initial maps
and the number plans in the initial collection.
We've used 100 maps generated with two different methods:

1. The first uses random maps from random spanning trees (RMfRST).
2. The second uses random maps from random starting points (RMfRSP).

These methods are described and implemented in the [rdatools/rdaensemble](https://github.com/rdatools/rdaensemble) repository.

We implemented the second initially, before realizing that we could simply use the 
conceptually simpler spanning-tree approach to generate the initial maps.
They yield similar results. 

## Installation

Clone the repository:

```bash
$ git clone https://github.com/alecramsay/rdaroot
$ cd rdaroot
```

There is no package to install, just a command line script to run.
However, you probably want to also clone the [rdatools/rdabase](https://github.com/alecramsay/rdabase) repository
for the data.

Note: This repository already has a `bin` directory with the `dccvt` executable in it
that is required by the [rdatools/rdadccvt](https://github.com/rdatools/rdadccvt) package.

## Usage

To heuristically search for an approximate root map,
generate an ensemble of contiguous maps with 'roughly equal' populations
using the [rdatools/rdaensemble](https://github.com/rdatools/rdaensemble)
and then run the search script like this:

```bash
scripts/approx_root_map.py \
    --state NC \
    --plans ~/iClound/ensembles/NC20C_RMfRST_100_plans.json \
    --data ../rdadata/data/NC/NC_2020_data.csv \
    --shapes ../rdadata/data/NC/NC_2020_shapes_simplified.json \
    --graph ../rdadata/data/NC/NC_2020_graph.json \
    --map ~/iCloud/fileout/rootmaps/NC20C_RMfRST_100_rootmap.csv \
    --candidates ~/iCloud/fileout/rootmaps/NC20C_RMfRST_100_rootcandidates.json \
    --log ~/iCloud/fileout/rootmaps/NC20C_RMfRST_100_rootlog.txt \
    --no-debug
```

The resulting precinct-assignment files (map) can be imported into [Dave's Redistricting](https://davesredistricting.org/) (DRA).

