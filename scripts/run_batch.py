#!/usr/bin/env python3

"""
RUN A BATCH OF COMMANDS

To run:

$ scripts/run_batch.py

"""

import os

import rdadata as rdautils

dccvt_py: str = "../dccvt/examples/redistricting"

# Generate random sites files for these plans

sample_plans: List[str] = [
    "{xx}_2020_Congress_Baseline.csv",
    "{xx}_2020_Congress_Proportional.csv",
    "{xx}_2020_Congress_Competitive.csv",
    "{xx}_2020_Congress_Minority.csv",
    "{xx}_2020_Congress_Compact.csv",
    "{xx}_2020_Congress_Splitting.csv",
]

#

xx: str = "NC"
points_csv: str = "temp/NC_2020_points.csv"
map_label: str = f"{xx}20C"
N: int = rdautils.DISTRICTS_BY_STATE[xx]["congress"]
K: int = 1  # district multiplier
fips: str = rdautils.STATE_FIPS[xx]

start: int = K * N * int(fips)

for i, seed in enumerate(range(start, start + 6)):
    output_csv: str = f"temp/{xx}_2020_randomsites_{i}.csv"

    command: str = f"python3 {dccvt_py}/redistricting.py randomsites --points {points_csv} --output {output_csv} --seed {seed} --N {N}"
    # command = command.format(xx=xx)
    print(command)
    os.system(command)

    break


### END ###
