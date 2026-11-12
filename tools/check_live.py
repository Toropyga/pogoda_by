"""Read-only provider smoke check, runnable without Home Assistant."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def load_parser():
    path = Path(__file__).resolve().parents[1] / "custom_components/pogoda_by/parser.py"
    spec = importlib.util.spec_from_file_location("pogoda_parser", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fetch(url):
    with urlopen(Request(url, headers={"Accept": "application/json, application/rss+xml"}), timeout=30) as response:
        body = response.read(4 * 1024 * 1024 + 1)
        if len(body) > 4 * 1024 * 1024:
            raise ValueError("Response too large")
        return body.decode(response.headers.get_content_charset() or "utf-8-sig")


def main():
    args_parser = argparse.ArgumentParser(description=__doc__)
    args_parser.add_argument("--country", default="BY")
    args_parser.add_argument("--station", default="26851")
    args = args_parser.parse_args()
    parser = load_parser()
    catalog = parser.normalize_catalog(json.loads(fetch("https://pogoda.by/api/v2/weather-fact/all-cities")))
    country = args.country.upper()
    if country not in catalog or args.station not in catalog[country]:
        raise ValueError("Selected station was not found in the country catalogue")
    station = catalog[country][args.station]
    observation = parser.parse_rss(fetch("https://pogoda.by/rss/weather?" + urlencode({"station": station.station_id})))
    print(json.dumps({
        "countries": sorted(catalog), "station_count": sum(map(len, catalog.values())),
        "station": station.as_dict(), "values": observation.values,
        "description": observation.description, "published": observation.published,
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"Provider check failed: {err}", file=sys.stderr)
        sys.exit(1)
