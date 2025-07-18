import json
import os
import re
import urllib.request
import warnings
from typing import Optional, Union

import ee

from ee_extra.utils import _load_JSON


def _get_apps(online: bool) -> dict:
    """Retrieves the dictionary of Google Earth Engine Apps from ee-appshot.
    Args:
        online : Whether to retrieve the most recent list of apps directly from the GitHub repository and not from the local copy.
    Returns:
        Apps.
    """
    if online:
        url = "https://raw.githubusercontent.com/samapriya/ee-appshot/main/app_urls.json"
        with urllib.request.urlopen(url) as url:
            apps = json.loads(url.read().decode())
    else:
        apps = _load_JSON("ee-appshot.json")

    return apps