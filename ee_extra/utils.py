import difflib
import json
import os
from typing import Any, Optional, Union, List

import pkg_resources


def _load_JSON(x: Optional[str] = "ee-catalog-ids.json") -> Any:
    """Loads the specified JSON file from the data directory.

    Args:
        x : JSON filename.

    Returns:
        JSON file.
    """
    eeExtraDir = os.path.dirname(
        pkg_resources.resource_filename("ee_extra", "ee_extra.py")
    )
    dataPath = os.path.join(eeExtraDir, "data/" + x)
    f = open(dataPath)
    data = json.load(f)

    return data


def _get_case_insensitive_close_matches(
    word: str, possibilities: List[str], n: int = 3, cutoff: float = 0.6
) -> List[str]:
    """A case-insensitive wrapper around difflib.get_close_matches.

    Args:
        word : A string for which close matches are desired.
        possibilites : A list of strings against which to match word.
        n : the maximum number of close matches to return. n must be > 0.
        cutoff : Possibilities that don't score at least that similar to word are ignored.

    Returns:
        The best (no more than n) matches among the possibilities are returned in a list,
        sorted by similarity score, most similar first.

    Examples:
        >>> from ee_extra.utils import _get_case_insensitive_close_matches
        >>> _get_case_insensitive_close_matches("mse", ["MSE", "ERGAS"])
        ["MSE"]
    """
    lower_matches = difflib.get_close_matches(
        word.lower(), [p.lower() for p in possibilities], n, cutoff
    )
    return [p for p in possibilities if p.lower() in lower_matches]
