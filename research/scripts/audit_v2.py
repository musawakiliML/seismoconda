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

def query_source(name: str, source: str, url: str) -> dict:
    """Query Source of URL

    Args:
        name (str): Name of package
        source (str): Package source(pypi, conda-forge, others)
        url (str): Package URL

    Returns:
        dict: JSON response
    """
    result = {
        "source": source,
        "url": url,
        "status": "unknown",
        "version": None,
        "error": None,
    }
    
    try:
        data = fetch_json(url=url)
        
        result["status"] = "found"
        
        if source == "pypi":
            result["version"] = data.get("info", {}).get("version")
            
        else:
            result["version"] = data.get("latest_version")
            
    except HTTPError as err:
        
        result["status"] = (
            "not_found" if err.code == 404 else "http_error"
        )
        
        result["error"] = str(err)
        
    except (URLError, TimeoutError, ValueError) as err:
        result["status"] = "request_error"
        result["error"] = str(err)
        
    return result

def audit_package(name: str, channels: list[str]) -> dict:
    """Audit Package from source

    Args:
        name (str): Package Name
        channels (list): List of sources to check

    Returns:
        dict: Json response with package details
    """
    sources = {}
    
    pypi_url = f"https://pypi.org/pypi/{name}/json"
    sources["pypi"] = query_source(name=name, source="pypi", url=pypi_url)
    
    for channel in channels:
        url = f"https://api.anaconda.org/package/{channel}/{name}"
        sources[channel] = query_source(name=name, source=channel, url=url)
        
    return {
        "package": name,
        "sources": sources,
    }

def main():
    """Main Function for auditing packages
    """
    
    results = [
        audit_package(name=name, channels=channels)
        for name, channels in PACKAGES.items()
    ]
    
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "packages": results,
    }
    
    output_path = Path("research/data/package_audit_v2.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_path.write_text(
        json.dumps(report, indent=2),
        enconding="utf-8"
        )
    for package in results:
        print(f"\nPackage: {package['package']}")
        
        for source, result in package["source"].items():
            print(
                f"Source: {source}, "
                f"Status: {result['status']}, "
                f"Version: {result['version']}, "
                f"Error: {result['error']}"
            )

if __name__ == "__main__":
    main()