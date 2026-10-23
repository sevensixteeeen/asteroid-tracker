"""Step 1: Get asteroid data from NASA's NeoWs API.

Run it with:  uv run fetch.py
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

import requests

# The "feed" endpoint lists asteroids that pass close to Earth between two dates.
FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"

# Use your own key if you've set the NASA_API_KEY environment variable,
# otherwise fall back to NASA's shared demo key (about 30 requests per hour).
API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")


def fetch_feed(start: date, end: date) -> dict:
    """Ask NASA for every near-Earth object between start and end (max 7 days)."""
    if (end - start).days > 7:
        raise ValueError("NASA's feed only allows a range of 7 days or less.")

    # These become the "?start_date=...&end_date=...&api_key=..." part of the URL.
    params = {
        "start_date": start.isoformat(),  # e.g. "2026-10-23"
        "end_date": end.isoformat(),
        "api_key": API_KEY,
    }

    # Send the GET request. The timeout stops the program from hanging forever
    # if NASA's server doesn't answer.
    response = requests.get(FEED_URL, params=params, timeout=30)

    # Status 200 means success. Anything else (403 bad key, 429 too many
    # requests, ...) raises an error here with a useful message.
    response.raise_for_status()

    # The body is JSON text; .json() turns it into Python dicts and lists.
    return response.json()


def save_json(data: dict, path: Path) -> None:
    """Save the raw response to a file so we can study it without calling the API again."""
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    start = date.today()
    end = start + timedelta(days=7)

    print(f"Asking NASA for asteroids from {start} to {end} (key: {API_KEY[:4]}...)")
    data = fetch_feed(start, end)

    out_file = Path("data") / "feed.json"
    save_json(data, out_file)
    print(f"Saved the full response to {out_file}\n")

    # --- A first look at the JSON ---
    # The top level is a dict. Let's see which keys it has.
    print("Top-level keys:", list(data.keys()))
    print("Total asteroids in this range:", data["element_count"])

    # "near_earth_objects" is a dict: each key is a date, each value is a list of asteroids.
    by_date = data["near_earth_objects"]
    for day in sorted(by_date):
        print(f"  {day}: {len(by_date[day])} asteroids")

    # Print one asteroid in full so you can see every field NASA gives us.
    first_day = sorted(by_date)[0]
    example = by_date[first_day][0]
    print(f"\nOne example asteroid ({example['name']}):")
    print(json.dumps(example, indent=2))
