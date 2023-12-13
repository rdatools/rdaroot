"""
MINIMIZE ENERGIES / MAXIMIZE POPULATION COMPACTNESS OF AN ENSEMBLE
"""

from typing import Any, Dict, List


def minimize_energies(
    plans: List[Dict[str, str | float | Dict[str, int | str]]],
    data: Dict[str, Dict[str, int | str]],
    shapes: Dict[str, Any],
    graph: Dict[str, List[str]],
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Minimize the energies / maximize the population compactness of an ensemble of maps."""

    ensemble_out: Dict[str, Any] = dict()

    return ensemble_out
