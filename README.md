# Asteroid Tracker

Track the near-Earth asteroids passing by this week, using NASA's free
[NeoWs](https://api.nasa.gov/) (Near Earth Object Web Service) API.

## Setup

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.12 and the
dependencies for you the first time you run anything:

```
uv sync
```

The scripts use NASA's shared `DEMO_KEY` by default, which allows about 30
requests an hour. For more, get a free key at https://api.nasa.gov/ and set it
before running:

```
# PowerShell
$env:NASA_API_KEY = "your-key-here"

# macOS / Linux
export NASA_API_KEY="your-key-here"
```

## Usage

| Step | Command | What it does |
|---|---|---|
| 1 | `uv run fetch.py` | Downloads the next 7 days of asteroids from NASA into `data/feed.json` |
| 2 | `uv run parse.py` | Flattens that JSON into `data/asteroids.csv` and prints the closest, biggest, fastest and hazardous ones |
| 3 | `uv run streamlit run app.py` | Opens the tracker in your browser at http://localhost:8501 |

The web page has a **Fetch latest from NASA** button, so once you're using it
you don't need to run steps 1 and 2 by hand.

## What's on the page

- Headline numbers: how many asteroids, the closest pass, the biggest, and how
  many NASA flags as potentially hazardous
- Filters for "only potentially hazardous" and "closer than X Moon distances"
- A chart of size against miss distance (hover a dot for details)
- A sortable table with a link to each asteroid's NASA JPL page

"Potentially hazardous" is NASA's label for asteroids that are large enough and
have orbits that come close enough to Earth's to be worth watching over the long
term. It doesn't mean this week's pass is dangerous.

## Deploy (Streamlit Community Cloud, free)

1. Sign in at https://share.streamlit.io with your GitHub account.
2. Click **Create app**, choose "Deploy a public app from GitHub", and pick this
   repo, branch `main`, main file `app.py`.
3. Open **Advanced settings**, choose Python **3.12**, and paste your NASA key
   into **Secrets**:

   ```toml
   NASA_API_KEY = "your-key-here"
   ```

4. Click **Deploy**. Community Cloud installs everything from `uv.lock`, and the
   app downloads this week's data from NASA on its first run.

Use your own key here, not `DEMO_KEY`: the demo key's hourly limit is shared,
so a hosted app runs out quickly.

## Files

- `fetch.py`: calls the NASA API and saves the raw response
- `parse.py`: turns the nested JSON into one flat row per asteroid
- `app.py`: the Streamlit web page
- `data/`: downloaded data (not committed to git)
