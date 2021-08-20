import json
import os
from typing import Any, Optional, Union

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
