import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# List of Packages to Audit

PACKAGES = {
    "obspy" : ["conda-forge"],
    "dascore" : ["conda-forge"],
    "seisbench" : ["conda-forge"],
    "pyrocko" : ["conda-forge", "pyrocko"],
    "eqcorrscan" : ["conda-forge"],
    "cartopy" : ["conda-forge"],
}

TIMEOUT = 15

def fetch_json(url: str) -> dict:
    """Fetch URL and return JSON response

    Args:
        url (str): Url to fetch

    Returns:
        dict: JSON response
    """
    
    request = Request(
        url,
        headers = {
            "User-Agent": "Seismoconda-Audit/0.1"
        },
    )
    
    with urlopen(request, timeout=TIMEOUT) as response:
        data = json.load(response)
        return data
    