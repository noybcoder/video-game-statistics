# Video Game Industry Analytics

An end-to-end data engineering pipeline that extracts video game data from the [IGDB API](https://api-docs.igdb.com/), transforms and loads it into a relational Postgres warehouse, serves it through a FastAPI analytics layer, and presents it through an interactive Streamlit dashboard — orchestrated with Airflow.

**Dashboard:** genre ratings over time, platform release trends, engine adoption among active developers, and developer genre specialization.

---

## Architecture

IGDB API
│ (paginated extraction, rate-limited)
▼
Parquet files (bronze layer)
│ (DuckDB: read, transform, cast, clean)
▼
Parquet files (silver layer)
│ (DuckDB → Postgres: bulk load)
▼
Postgres (schema, constraints, indexes via psycopg2)
│
├─▶ FastAPI (analytics endpoints)
│ │
│ ▼
│ Streamlit (multipage dashboard)
│
└─▶ Airflow (orchestrates the full pipeline above)


**Why this split between DuckDB and psycopg2:** DuckDB's Postgres extension is excellent for bulk data movement (`CREATE TABLE ... AS SELECT`, `INSERT ... SELECT`) but does not reliably support schema-altering DDL against an attached Postgres catalog — attempting constraints or indexes through it fails with `BindAlterAddIndex not supported by this catalog`. Table creation and bulk loading go through DuckDB; primary keys, foreign keys, indexes, and views are created afterward through direct `psycopg2` connections.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Extraction | Python, `requests` |
| Transformation / Load | DuckDB |
| Warehouse | PostgreSQL |
| Schema / constraints / indexes | psycopg2 |
| API | FastAPI |
| Dashboard | Streamlit, Plotly |
| Orchestration | Apache Airflow |

---

## Data Model

Core entity tables: `games`, `genres`, `platforms`, `companies`, `game_engines`.
Junction tables (many-to-many): `games_genres`, `games_platforms`, `companies_developed`, `companies_published`, `games_game_engines`.

Junction tables use composite primary keys `(entity_a_id, entity_b_id)` with `ON DELETE CASCADE` foreign keys to both parent tables. Since a composite primary key only efficiently supports lookups on its leading column, a supplementary single-column index is added on the second key of each junction table to support independent lookups (e.g., filtering by `platform_id` without also filtering by `game_id`).

A composite index on `games(total_rating_count, release_year)` supports the filter pattern shared by every analytics query in this project.

A reusable Postgres **view**, `active_developers`, encodes the "active developer" definition (below) once, rather than repeating the logic across every query that needs it.

---

## Data Quality Decisions

Raw IGDB data includes a very large volume of low-substance, unrated content (mass-produced adult titles, asset-flip shovelware, single-developer proprietary-engine test projects). Without filtering, this content dominates naive aggregate counts and produces misleading results.

**Finding:** comparing genre distribution with and without a minimum rating-engagement filter showed genres like *Indie* and *Visual Novel* inflating over 100x when unfiltered — driven almost entirely by mass-produced content with zero player engagement (`total_rating_count IS NULL`), not genuine catalog diversity.

**Resulting thresholds, applied consistently across the pipeline's analytics queries:**
- `total_rating_count >= 30` — a game must have at least 30 individual ratings before its `total_rating` is treated as statistically reliable. This is a fixed, global threshold, since the reliability of an individual rating doesn't depend on genre or release year.
- **"Active developer"** (the `active_developers` view) — a developer with at least 5 qualifying games (rating-count ≥ 30) released in the last 15 years, including at least one release in the last 3 years. This filters out both one-hit-wonder and now-defunct studios, and — critically — the high-volume, zero-engagement shovelware studios the rating-count filter alone doesn't catch at the developer level.
- **Genre rankings** use a rating-count-**weighted** average (`SUM(rating * rating_count) / SUM(rating_count)`), not a plain average — a game with a large rating base should influence a genre's score more than a game with a handful of ratings. This is an audience-reception metric.
- **Engine popularity** uses raw adoption counts (games and distinct developers), not a weighted rating — "popularity" here is a measure of developer tooling choice, not audience sentiment, so a rating-weighted average would answer a different question than the one being asked.

---

## Dashboard

| Page | Content | Chart type |
|---|---|---|
| Overview | Genre distribution across the dataset (top 8 genres + "Others", by cumulative share) | Pie chart |
| Audience & Quality | Top-10-ranked genres by weighted average rating, per year (last 15 years) | Heatmap |
| Platforms | Release volume for the top 15 platforms by total games, per year | Heatmap |
| Developer Insights | Top game engines by adoption among active developers; each active developer's dominant genre specialization | Grouped bar chart + filterable table |

---

## Orchestration

The pipeline is orchestrated with Airflow. The DAG structure:

extract_igdb_data
│
├──▶ load_games ──┐
├──▶ load_genres ─┤
├──▶ load_platforms ┤──▶ load_junction_tables ──▶ create_constraints_and_indexes ──▶ create_views
├──▶ load_companies ┤
└──▶ load_engines ──┘


Entity tables load in parallel, since they're independent of each other. Junction tables wait for both entity tables they reference. Constraints and indexes run last, once all tables are populated.

The DAG is configured with a `@weekly` schedule interval — appropriate given IGDB's catalog doesn't change meaningfully day to day, and re-extracting the full dataset daily would be unnecessary load against IGDB's rate limits. For local development, runs are triggered manually; in a hosted deployment (a persistent VM or a managed Airflow service), the scheduler would execute automatically on that cadence.

---

## Setup

### Prerequisites
- Python 3.12+
- Docker (for Postgres)
- An IGDB API client ID and access token

### 1. Environment variables
Copy `.env.example` to `.env` and fill in:

IGDB_CLIENT_ID=
IGDB_ACCESS_TOKEN=
POSTGRES_DATABASE_HOST=localhost
POSTGRES_DATABASE_PORT=5432
POSTGRES_DATABASE_USER=postgres
POSTGRES_DATABASE_PASSWORD=
POSTGRES_DATABASE_NAME=video_games


### 2. Start Postgres
```bash
docker run --name video-games -e POSTGRES_PASSWORD='<password>' -p 5432:5432 -v postgres_data:/var/lib/postgresql -d postgres
```

### 3. Run the pipeline
```bash
python extract/run_extract.py     # IGDB → bronze parquet
python transform_load/transform.py # bronze → silver parquet (DuckDB)
python transform_load/load.py      # silver parquet → Postgres, schema, constraints, indexes
```

### 4. Start the API
```bash
uvicorn api.main:app --reload --port 8000
```

### 5. Start the dashboard
```bash
streamlit run dashboard/Overview.py
```

---

## Testing

A small suite of targeted tests covers the highest-risk logic: schema-generation utilities, and a smoke test per API endpoint confirming correct response shape via FastAPI's `TestClient`.

```bash
pytest tests/
```

---

## Possible Extensions

- Publisher data (extracted but not currently visualized) — comparing developer vs. publisher activity, or overlap between the two
- Platform × genre relationship analysis
- Materialized views for the more expensive aggregate queries, refreshed after each pipeline run
- Hosted deployment (managed Airflow + RDS) for genuine unattended scheduled execution