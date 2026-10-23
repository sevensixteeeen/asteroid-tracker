"""Step 3: A web page for exploring this week's asteroids.

Run it with:  uv run streamlit run app.py
"""

from datetime import date, timedelta

import altair as alt
import pandas as pd
import streamlit as st

from background import SPACE, add_space_background
from fetch import fetch_feed, save_json
from parse import IN_FILE, load_rows

st.set_page_config(page_title="Asteroid Tracker", page_icon="☄️", layout="wide")
add_space_background()

# Two colors for the chart: one for ordinary asteroids, one for the ones NASA
# flags as potentially hazardous. Dark mode gets slightly adjusted shades so
# both stay easy to see on a dark background.
# "ring" is a thin outline in the background color that keeps overlapping dots
# apart, and "grid" is kept faint so the gridlines don't compete with the dots.
COLORS = {
    "light": {"Not hazardous": "#2a78d6", "Potentially hazardous": "#eb6834", "ring": "#fcfcfb", "grid": "#e1e0d9"},
    "dark": {"Not hazardous": "#3987e5", "Potentially hazardous": "#d95926", "ring": SPACE, "grid": "#1f2638"},
}


# st.cache_data remembers the result, so the file is only read again when we
# clear the cache (after fetching new data) instead of on every click.
@st.cache_data
def load_table() -> pd.DataFrame:
    """Load the saved feed as a pandas DataFrame, the table type Streamlit understands."""
    df = pd.DataFrame(load_rows(IN_FILE))
    # Turn "2026-Oct-28 16:15" into a real date-time so the table sorts by time.
    df["approach_time"] = pd.to_datetime(df["approach_time"], format="%Y-%b-%d %H:%M")
    df["group"] = df["hazardous"].map({True: "Potentially hazardous", False: "Not hazardous"})
    return df.sort_values("miss_distance_km").reset_index(drop=True)


def fetch_latest() -> None:
    """Download the next 7 days from NASA and save over data/feed.json."""
    start = date.today()
    save_json(fetch_feed(start, start + timedelta(days=7)), IN_FILE)
    load_table.clear()  # forget the old table so the new file gets read


# --- Sidebar: get fresh data ---
with st.sidebar:
    st.header("Data")
    if st.button("Fetch latest from NASA", width="stretch"):
        with st.spinner("Asking NASA..."):
            try:
                fetch_latest()
                st.success("Updated!")
            except Exception as error:  # e.g. no internet, or the demo key's hourly limit
                st.error(f"Couldn't fetch new data: {error}")
    st.caption("Uses the NASA_API_KEY environment variable, or NASA's shared demo key.")

# The data folder isn't saved in git, so a fresh copy of the app (like one
# deployed to Streamlit Community Cloud) starts with no file. Fetch it once.
if not IN_FILE.exists():
    with st.spinner("First run: downloading this week's asteroids from NASA..."):
        try:
            fetch_latest()
        except Exception as error:
            st.error(f"Couldn't download data from NASA: {error}")
            st.stop()

df = load_table()

st.title("☄️ Asteroid Tracker")
first, last = df["approach_time"].min(), df["approach_time"].max()
st.caption(f"Near-Earth asteroids passing between {first:%b %d} and {last:%b %d, %Y}, from NASA NeoWs.")

# --- Headline numbers ---
closest = df.iloc[0]  # the table is sorted by miss distance, so row 0 is the closest
biggest = df.loc[df["diameter_max_m"].idxmax()]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Asteroids this week", len(df))
# The small line under each number names the asteroid. delta_arrow="off" hides
# the up/down arrow Streamlit normally draws there, since this isn't a change.
col2.metric(
    "Closest pass (Moon distances)",
    f"{closest['miss_distance_lunar']:.1f}",
    closest["name"],
    delta_color="off",
    delta_arrow="off",
)
col3.metric(
    "Biggest (max diameter)",
    f"{biggest['diameter_max_m']:,.0f} m",
    biggest["name"],
    delta_color="off",
    delta_arrow="off",
)
col4.metric("Potentially hazardous", int(df["hazardous"].sum()))

# --- Filters (they apply to both the chart and the table) ---
f1, f2 = st.columns([1, 2])
only_hazardous = f1.toggle("Only potentially hazardous")
max_lunar = f2.slider(
    "Closer than (Moon distances)",
    min_value=0,
    max_value=int(df["miss_distance_lunar"].max()) + 1,
    value=int(df["miss_distance_lunar"].max()) + 1,
)

shown = df[df["miss_distance_lunar"] <= max_lunar]
if only_hazardous:
    shown = shown[shown["hazardous"]]

if shown.empty:
    st.warning("No asteroids match these filters.")
    st.stop()

# --- Chart: how big is each asteroid, and how close does it come? ---
st.subheader("Size vs. how close it comes")
st.caption("Each dot is one asteroid. Further left means closer to Earth; higher means bigger. Hover a dot for details.")

palette = COLORS["dark" if st.context.theme.type == "dark" else "light"]
groups = ["Not hazardous", "Potentially hazardous"]

chart = (
    alt.Chart(shown)
    .mark_circle(size=90, opacity=0.9, stroke=palette["ring"], strokeWidth=2)
    .encode(
        x=alt.X(
            "miss_distance_lunar:Q",
            title="Miss distance (Moon distances)",
            scale=alt.Scale(zero=True),
            axis=alt.Axis(tickCount=8, gridColor=palette["grid"]),  # about one label per 25
        ),
        # Sizes range from a few meters to over a kilometer, so a log scale keeps
        # the small ones from all piling up at the bottom.
        # nice=False stops the axis rounding up to the next power of ten (10,000 m),
        # and listing the tick values stops the extra gridlines in between.
        y=alt.Y(
            "diameter_max_m:Q",
            title="Estimated diameter, max (m)",
            scale=alt.Scale(type="log", nice=False, padding=12),
            axis=alt.Axis(values=[10, 30, 100, 300, 1000], format=",", gridColor=palette["grid"]),
        ),
        color=alt.Color(
            "group:N",
            title=None,
            scale=alt.Scale(domain=groups, range=[palette[g] for g in groups]),
            legend=alt.Legend(orient="top"),
        ),
        tooltip=[
            alt.Tooltip("name:N", title="Name"),
            alt.Tooltip("approach_time:T", title="Closest approach", format="%b %d, %H:%M"),
            alt.Tooltip("diameter_min_m:Q", title="Diameter min (m)", format=",.0f"),
            alt.Tooltip("diameter_max_m:Q", title="Diameter max (m)", format=",.0f"),
            alt.Tooltip("speed_km_s:Q", title="Speed (km/s)", format=".1f"),
            alt.Tooltip("miss_distance_lunar:Q", title="Moon distances", format=".1f"),
            alt.Tooltip("miss_distance_km:Q", title="Miss distance (km)", format=",.0f"),
        ],
    )
    .properties(height=420)
)
st.altair_chart(chart, width="stretch")

# --- Table: every asteroid, sortable by clicking a column header ---
st.subheader(f"All {len(shown)} asteroids")
# Round the sizes to whole meters so "localized" shows them as 1,164 rather than 1,164.2.
table = shown.drop(columns=["id", "group"]).round({"diameter_min_m": 0, "diameter_max_m": 0})
st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    column_config={
        "name": "Name",
        "approach_time": st.column_config.DatetimeColumn("Closest approach", format="MMM D, HH:mm"),
        "diameter_min_m": st.column_config.NumberColumn("Diameter min (m)", format="localized"),
        "diameter_max_m": st.column_config.NumberColumn("Diameter max (m)", format="localized"),
        "speed_km_s": st.column_config.NumberColumn("Speed (km/s)", format="%.1f"),
        "miss_distance_km": st.column_config.NumberColumn("Miss distance (km)", format="localized"),
        "miss_distance_lunar": st.column_config.NumberColumn("Moon distances", format="%.1f"),
        "hazardous": st.column_config.CheckboxColumn("Hazardous?"),
        "jpl_url": st.column_config.LinkColumn("NASA JPL", display_text="details"),
    },
)
