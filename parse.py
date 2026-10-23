"""Step 2: Turn NASA's nested JSON into a flat table, one row per asteroid.

Run fetch.py first, then:  uv run parse.py
"""

import csv
import json
from pathlib import Path

IN_FILE = Path("data") / "feed.json"
OUT_FILE = Path("data") / "asteroids.csv"


def flatten(asteroid: dict) -> dict:
    """Pick out the fields we care about from one asteroid and make them real numbers."""
    # The feed only includes the close approach that falls inside our date range,
    # so this list has one entry. We take the first one.
    approach = asteroid["close_approach_data"][0]
    size = asteroid["estimated_diameter"]["meters"]

    # Some names are wrapped in brackets, "(2007 UP6)". Others have a catalog
    # number in front, "516803 (2010 JG88)", and those we leave alone.
    name = asteroid["name"]
    if name.startswith("(") and name.endswith(")"):
        name = name[1:-1]

    # NASA sends distances and speeds as text ("34512866.50..."), so we use
    # float() to turn them into numbers we can sort and compare.
    return {
        "id": asteroid["id"],
        "name": name,
        "approach_time": approach["close_approach_date_full"],
        "diameter_min_m": round(size["estimated_diameter_min"], 1),
        "diameter_max_m": round(size["estimated_diameter_max"], 1),
        "speed_km_s": round(float(approach["relative_velocity"]["kilometers_per_second"]), 2),
        "miss_distance_km": round(float(approach["miss_distance"]["kilometers"])),
        "miss_distance_lunar": round(float(approach["miss_distance"]["lunar"]), 2),
        "hazardous": asteroid["is_potentially_hazardous_asteroid"],
        "jpl_url": asteroid["nasa_jpl_url"],
    }


def load_rows(path: Path) -> list[dict]:
    """Read the saved feed and return a flat list of asteroid rows."""
    data = json.loads(path.read_text(encoding="utf-8"))

    rows = []
    # "near_earth_objects" groups asteroids by date. We don't need the grouping
    # any more, because every row already has its own approach time.
    for asteroids_on_day in data["near_earth_objects"].values():
        for asteroid in asteroids_on_day:
            rows.append(flatten(asteroid))
    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    """Save the table as a CSV file, which opens in Excel or Google Sheets."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    rows = load_rows(IN_FILE)
    save_csv(rows, OUT_FILE)
    print(f"Turned {len(rows)} asteroids into a table and saved it to {OUT_FILE}\n")

    # --- Now that the data is flat, questions become one line each ---

    # Sort by miss distance: the smallest number is the closest pass.
    closest = sorted(rows, key=lambda r: r["miss_distance_km"])
    print("The 10 closest passes:")
    print(f"  {'Name':<20} {'When':<18} {'Size (m)':>12} {'km/s':>6} {'Moon distances':>15}")
    for r in closest[:10]:
        size = f"{r['diameter_min_m']:.0f}-{r['diameter_max_m']:.0f}"
        flag = "  HAZARDOUS" if r["hazardous"] else ""
        print(
            f"  {r['name']:<20} {r['approach_time']:<18} {size:>12} "
            f"{r['speed_km_s']:>6.1f} {r['miss_distance_lunar']:>15.1f}{flag}"
        )

    biggest = max(rows, key=lambda r: r["diameter_max_m"])
    fastest = max(rows, key=lambda r: r["speed_km_s"])
    hazardous = [r for r in rows if r["hazardous"]]

    print(f"\nBiggest: {biggest['name']}, up to {biggest['diameter_max_m']:.0f} m across")
    print(f"Fastest: {fastest['name']}, {fastest['speed_km_s']} km/s")
    print(f"Flagged potentially hazardous by NASA: {len(hazardous)} of {len(rows)}")
    for r in hazardous:
        print(f"  {r['name']} passes at {r['miss_distance_lunar']:.1f} Moon distances")
