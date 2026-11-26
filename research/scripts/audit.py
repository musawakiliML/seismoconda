import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# List of Pakcages to Audit
PACKAGES = [
    "obspy",
    "dascore",
    "seisbench",
    "pyrocko",
    "eqcorrscan",
    "cartopy",
]

CHANNEL = "conda-forge"

def fetch_pakcage_info(name: str) -> dict:
    """Fetch packages info from anaconda

    Args:
        name (str): Package name

    Returns:
        dict: package details
    """
    
    url = f"https://api.anaconda.org/package/{CHANNEL}/{name}"
    
    try:
        with urlopen(url, timeout=15) as response:
            data = json.load(response)
            
            return {
                "package": name,
                "channel": CHANNEL,
                "status": "found",
                "latest_version": data.get("latest_version"),
                "error": None,
            }
    except HTTPError as err:
        
        status = "not_found" if err.code == 404 else "http_error"
        
        return {
            "package": name,
            "channel": CHANNEL,
            "status": status,
            "latest_version": None,
            "error": str(err),
        }
    except (URLError, TimeoutError, ValueError) as err:
        
        return {
            "package": name,
            "channel": CHANNEL,
            "status": "request_error",
            "latest_version": None,
            "error": str(err),
        }

def main():
    
    results = [fetch_pakcage_info(name=name) for name in PACKAGES]
    
    output = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "results": results
    }
    
    path = "research/data/package_audit.json"
    
    with open(path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)
        
    for item in results:
        print(
            item["package"],
            item["status"],
            item["latest_version"],
        )

if __name__ == "__main__":
    main()    