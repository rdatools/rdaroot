"""
HELPERS - Bits & pieces used by multiple scripts.
"""

from typing import List

import os
from rdadata import temp_dir


### WORKING FILES ###

# TODO - DELETE
# working_dir: str = "temp"

files: List[str] = [
    "dccvt.points.csv",
    "dccvt.adjacencies.csv",
    "dccvt.randomsites.csv",
    "dccvt.randommap.csv",
    "dccvt.initial.csv",
    "dccvt.balzer1.csv",
    "dccvt.contiguous.csv",
    "dccvt.balzer2.csv",
    "dccvt.consolidated.csv",
    "dccvt.complete.csv",
    "dccvt.out.csv",
]
file_list: List[str] = [f"{temp_dir}/{f}" for f in files]

(
    dccvt_points,
    dccvt_adjacencies,
    dccvt_randomsites,
    dccvt_randommap,
    dccvt_initial,
    dccvt_balzer1,
    dccvt_contiguous,
    dccvt_balzer2,
    dccvt_consolidated,
    dccvt_complete,
    dccvt_output,
) = file_list

### CONSTANTS ###

# TODO - DELETE
# roughly_equal: float = 0.02

### FUNCTIONS ###

# TODO - DELETE
# def starting_seed(xx: str, N: int, K: int = 1) -> int:
#     fips: str = rdautils.STATE_FIPS[xx]
#     start: int = K * N * int(fips)

#     return start


def clean(file_list: List[str]) -> None:
    for f in file_list:
        if f in [dccvt_points, dccvt_adjacencies]:
            continue
        if os.path.exists(f):
            os.remove(f)


### END ###
