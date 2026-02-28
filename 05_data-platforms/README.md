# Module 5: Data Platforms

These are my notes on Module 5 of the Data Engineering Zoomcamp, covering data platforms and end-to-end pipeline building with Bruin.

---

## Installation

### Bruin CLI

Install the Bruin CLI (works on GitHub Codespaces / Linux):

```bash
curl -LsSf https://getbruin.com/install/cli | sh
source ~/.bashrc
```

Verify the installation:

```bash
bruin version
# Current: v0.0.0-test (392f275c9064399fc263d2da3de811210c6dc76f)
```

### VS Code Extension

Install the **Bruin** extension from the VS Code marketplace. It adds a Bruin panel to the IDE for running assets and pipelines, viewing lineage, and rendering queries directly from the editor.

### Bruin MCP (AI Agent Integration)

MCP (Model Context Protocol) lets a VS Code AI agent communicate directly with Bruin — running commands, validating pipelines, querying data, and creating assets on your behalf.

> **Note:** Since I am using **Antigravity** as  AI assistant, we don't strictly need MCP — Antigravity already has direct access to the project and can run Bruin commands on its own. However, we set it up anyway in case we switch to another agent like GitHub Copilot or Cursor AI, which do require MCP to interact with Bruin.

To enable it, create `.vscode/mcp.json` at the root of the project:

```json
{
  "servers": {
    "bruin": {
      "command": "bruin",
      "args": ["mcp"]
    }
  }
}
```

Once configured, the AI agent in VS Code will have direct access to your Bruin project.

---

## Project Initialization

### Why Bruin needs Git

Bruin requires the project folder to be a git repository. It uses git to:

- Detect the root of the project
- Track changes to assets and pipelines
- Automatically add `.bruin.yml` to `.gitignore` to prevent credentials/secrets from being pushed to GitHub

Since the workspace is already a git repo, there's no need to initialize it separately — Bruin detects it automatically.

### Initializing a Bruin project

```bash
bruin init default bruin-pipeline
```

This creates a new project from the `default` template inside the `bruin-pipeline/` folder. The structure looks like:

```text
bruin-pipeline/
├── .bruin.yml        # Environment and connection config (gitignored — contains secrets)
├── pipeline.yml      # Pipeline name, schedule, default connections
└── assets/
    └── ...           # Asset files (SQL, Python, YAML)
```

> To validate the project structure right away:
> ```bash
> bruin validate bruin-pipeline
> ```

---

## Configuration Files

Bruin uses two separate config files that work together but have different responsibilities:

| | `.bruin.yml` | `pipeline.yml` |
|---|---|---|
| **What it defines** | Which connections *exist* and their credentials | Which connection this pipeline uses by default |
| **How many** | One per workspace (global) | One per pipeline |
| **Goes to git?** | ❌ No (added to `.gitignore`) | ✅ Yes |
| **Contains secrets?** | ✅ Yes (paths, passwords, API keys) | ❌ No (only names/aliases) |
| **Managed by** | The environment admin | The pipeline developer |

> **Key idea:** `.bruin.yml` is the *registry* of available connections. `pipeline.yml` simply picks which one to use. This way, if credentials change, you update one file — all pipelines keep working without any changes.

---

### `.bruin.yml` — Environments & Connections

This file lives at the **root of the workspace** and is automatically added to `.gitignore` — it should **never be pushed to the repo** since it contains connection credentials and secrets.

It defines environments (e.g. `default`, `production`, `staging`) and the connections available in each. Our current setup:

```yaml
default_environment: default
environments:
    default:
        connections:
            duckdb:
                - name: duckdb-default
                  path: duckdb.db       # local database file, created on first run
            chess:
                - name: chess-default
                  players:
                    - MagnusCarlsen
                    - Hikaru
```

- **`duckdb-default`** — points to a local `duckdb.db` file on disk. DuckDB is an embedded analytical database (no server needed — just a file). The `.db` file doesn't exist yet; **Bruin creates it automatically the first time the pipeline runs**.
- **`chess-default`** — connects to the public Chess.com API for the listed players. This is the data **source**.

The connection names (`duckdb-default`, `chess-default`) are just aliases — what matters is that they match the names referenced in `pipeline.yml` and the asset files.

---

### `pipeline.yml` — Pipeline Configuration

Defines the global settings for the pipeline. All assets inside the pipeline inherit these defaults.

```yaml
name: bruin-init        # identifier shown in logs and the Bruin panel
schedule: daily         # how often to run (also: hourly, weekly, or cron expressions)
start_date: "2023-03-20" # earliest date Bruin will process data for
catchup: false          # if false, skips missed runs (like Airflow's catchup=False)

default_connections:
    duckdb: "duckdb-default"  # all assets use this DuckDB connection by default
```

The `start_date` is important for **incremental ingestion** — Bruin uses it to know the boundary for time-based data processing. Assets can override the default connection if needed.

---

## Assets

The `assets/` folder contains the actual data scripts. Each asset is a self-contained unit of work (ingestion, transformation, query). Asset types:

| Type | Example | Purpose |
|------|---------|---------|
| **YAML (ingestr)** | `players.asset.yml` | Declarative ingestion from a source to a destination |
| **SQL** | `player_stats.sql` | SQL transformations with optional quality checks |
| **Python** | `my_python_asset.py` | Custom logic in Python |

### Dependencies and execution order

Assets can declare dependencies on each other using the `depends` field. Bruin builds a **lineage graph** from these declarations and runs assets in the correct order automatically — when an upstream asset finishes, it triggers the downstream ones.

In our pipeline:

```
dataset.players  (players.asset.yml)   ←  runs first (ingestion from Chess.com)
       ↓
dataset.player_stats  (player_stats.sql)  ←  runs after, reads from dataset.players
```

The dependency is declared in `player_stats.sql`:

```sql
/* @bruin
name: dataset.player_stats
type: duckdb.sql
materialization:
  type: table

depends:
   - dataset.players    -- ← Bruin will not run this until dataset.players is done
@bruin */

SELECT name, count(*) AS player_count
FROM dataset.players
GROUP BY 1
```

In short, `player_stats.sql` reads from `dataset.players` (populated by the Chess.com ingestion asset) and groups records by player name, producing a count of entries per player stored as the `dataset.player_stats` table in DuckDB. Since it declares `dataset.players` as a dependency, Bruin always runs it after ingestion completes. On top of the SQL, it runs built-in and custom data quality checks automatically after the query finishes.

The asset also defines **quality checks** on the output columns (e.g. `not_null`, `unique`, `positive`) and a **custom check** that verifies the result table is not empty — Bruin runs these automatically after the query completes.

---

## Running a Pipeline

To run a specific asset:

```bash
bruin run \
  --start-date 2026-02-25T00:00:00.000Z \
  --end-date 2026-02-25T23:59:59.999999999Z \
  --environment default \
  "bruin-pipeline/assets/players.asset.yml"
```

### Built-in date interval variables

One of Bruin's key features is the built-in `start_date` and `end_date` interval variables. These are passed to every asset run and control the time window for data ingestion — without any extra configuration.

For example, to ingest data for the entire year 2025:

```bash
bruin run \
  --start-date 2025-01-01T00:00:00.000Z \
  --end-date 2025-12-30T23:59:59.999999999Z \
  --environment default \
  "bruin-pipeline/assets/players.asset.yml"
```

Built-in ingestor assets (YAML type) automatically use these dates for **incremental ingestion** — only fetching data within the specified window, rather than re-loading everything from scratch every time.

### What happens internally

When we ran `players.asset.yml` for the first time, Bruin executed three phases internally:

| Phase | What it does |
|-------|-------------|
| **Extract** | Called the Chess.com API and fetched profiles for the configured players |
| **Normalize** | Converted the raw JSON response into the correct columnar format for DuckDB |
| **Load** | Wrote the data to `duckdb / dataset.players` in the local `duckdb.db` file |

> **Note:** The `duckdb.db` file did **not exist** before this run — Bruin created it automatically during the Load phase.

### Running dependent assets

Once `dataset.players` is loaded, we can run the downstream SQL asset. Because `dataset.player_stats` declares `dataset.players` as a dependency, Bruin knows to run them in order. You can trigger the full chain with `--downstream`:

```bash
bruin run --downstream \
  --start-date 2025-01-01T00:00:00.000Z \
  --end-date 2025-12-30T23:59:59.999999999Z \
  "bruin-pipeline/assets/players.asset.yml"
```

Or run `player_stats` on its own (after `players` has already been loaded):

```bash
bruin run "bruin-pipeline/assets/player_stats.sql"
```

### Querying the results

Once the pipeline has run, you can query the data directly via the Bruin CLI:

```bash
bruin query --connection duckdb-default --query "SELECT * FROM dataset.players LIMIT 10"
bruin query --connection duckdb-default --query "SELECT * FROM dataset.player_stats"
```

---

## NYC Taxi Pipeline (End-to-End)

This section covers building a full three-layer pipeline using NYC Taxi data and DuckDB, following the Bruin zoomcamp template.

### Architecture

The pipeline is structured in three layers:

1. **Ingestion** — extract raw data and load it into the database as-is
2. **Staging** — clean, transform, deduplicate, and join with lookup tables
3. **Reports** — aggregate data into summary tables for analysis

All assets declare dependencies on each other, so Bruin builds a lineage graph and runs them in the correct order automatically.

### Project Setup

```bash
bruin init zoomcamp my-taxi-pipeline
```

This initialises the project from the `zoomcamp` template, which includes a pre-built three-layer folder structure under `pipeline/assets/` (ingestion, staging, reports) with placeholder assets ready to fill in.

The first thing we configure is `pipeline.yml`, which defines the global settings for the entire pipeline:

```yaml
name: nyc-taxi          # shown in logs and exposed as BRUIN_PIPELINE to Python assets
schedule: daily         # pipeline runs once a day
start_date: "2022-01-01"  # earliest date used when doing a full-refresh backfill

default_connections:
  duckdb: duckdb-default  # all assets use this DuckDB connection unless they override it

variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow"]   # which taxi types to ingest; can be overridden with --var at runtime
```

- **`name`** — a human-readable identifier that appears in Bruin logs and is injected as the `BRUIN_PIPELINE` environment variable inside Python assets.
- **`schedule`** — tells Bruin how often to run the pipeline automatically. Here `daily` means once per day.
- **`start_date`** — the earliest date Bruin will consider when running a full refresh. Data before this date is never processed.
- **`default_connections`** — sets `duckdb-default` as the default DuckDB connection for every asset in the pipeline, so individual assets don't need to repeat it.
- **`variables`** — pipeline-level variables defined using JSON Schema. `taxi_types` is an array of strings defaulting to `["yellow"]`. It can be overridden at runtime (e.g. `--var taxi_types='["yellow","green"]'`) and is read inside Python assets via the `BRUIN_VARS` environment variable.

### Ingestion Layer

The ingestion layer is responsible for pulling raw data from external sources and landing it in the database **as-is**, without any cleaning or transformations. There are two assets:

1. **`trips.py`** — Python asset that fetches NYC Taxi parquet files from the TLC public endpoint
2. **`payment_lookup.asset.yml`** — Seed asset that loads a static CSV lookup table

#### Python asset: `trips.py`

The Bruin header is embedded inside the Python docstring at the top of the file:

```python
"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append
@bruin"""
```

- **`type: python`** — tells Bruin this is a Python asset (as opposed to SQL or YAML)
- **`image: python:3.11`** — Bruin runs Python assets in an isolated environment using this image, so we never pollute the host machine
- **`connection: duckdb-default`** — the destination where the returned DataFrame will be loaded
- **`materialization: type: table / strategy: append`** — each run *appends* new rows to the `ingestion.trips` table without touching existing rows. We keep raw data accumulating here; deduplication happens downstream in the staging layer

#### `requirements.txt`

Python dependencies for the asset are declared in a `requirements.txt` file in the same folder:

```
pandas==2.2.0
requests==2.31.0
pyarrow==15.0.0
python-dateutil==2.8.2
```

**Bruin handles this automatically** — when it runs the asset, it reads `requirements.txt` and installs the packages into an isolated environment before executing the script. You don't need to install anything manually.


#### The `materialize()` function

Instead of writing SQL to insert data, we define a `materialize()` function that **returns a DataFrame** — Bruin takes care of the actual insert:

```python
def materialize():
    start_date = datetime.strptime(os.environ["BRUIN_START_DATE"], "%Y-%m-%d")
    end_date   = datetime.strptime(os.environ["BRUIN_END_DATE"],   "%Y-%m-%d")
    taxi_types = json.loads(os.environ.get("BRUIN_VARS", "{}")).get("taxi_types", ["yellow"])

    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"

    frames = []
    for taxi_type in taxi_types:
        current = start_date.replace(day=1)      # snap to first of month
        while current <= end_date:
            url = f"{base_url}/{taxi_type}_tripdata_{current:%Y}-{current:%m}.parquet"
            df  = pd.read_parquet(io.BytesIO(requests.get(url).content))
            df["taxi_type"]    = taxi_type
            df["extracted_at"] = datetime.utcnow().isoformat()
            frames.append(df)
            current += relativedelta(months=1)

    return pd.concat(frames, ignore_index=True)
```

Key points:

| Detail | Why |
|--------|-----|
| `BRUIN_START_DATE` / `BRUIN_END_DATE` | Bruin injects the run's date window as env vars; we use them to know which monthly parquet files to download |
| `BRUIN_VARS` | Pipeline variables (like `taxi_types`) are passed as a JSON string in this env var |
| Snap `start_date` to first of month | TLC publishes one file per calendar month, so we always start at the 1st |
| `taxi_type` column | Added so we can filter by taxi type in staging / reports |
| `extracted_at` column | A lineage/debugging column that records when each batch was fetched |
| Return a DataFrame | Bruin materialises it into the destination automatically — no manual SQL inserts needed |

#### How `materialize()` works — step by step

**The big picture:** Bruin calls `materialize()` and expects a DataFrame back. It then handles inserting that data into `ingestion.trips` using the `append` strategy. You don't write any SQL — you just return data.

**Step 1 — Read the run context from env vars**

```python
start_date = datetime.strptime(os.environ["BRUIN_START_DATE"], "%Y-%m-%d")
end_date   = datetime.strptime(os.environ["BRUIN_END_DATE"],   "%Y-%m-%d")
taxi_types = json.loads(os.environ.get("BRUIN_VARS", "{}")).get("taxi_types", ["yellow"])
```

When Bruin runs the asset it injects these env variables automatically:
- `BRUIN_START_DATE` — e.g. `"2022-01-01"`
- `BRUIN_END_DATE` — e.g. `"2022-03-01"`
- `BRUIN_VARS` — e.g. `'{"taxi_types": ["yellow"]}'` — the pipeline variable from `pipeline.yml`

**Step 2 — Figure out which files to download**

```python
current = start_date.replace(day=1)   # always start at day 1 of the month
while current <= end_date:
    url = f"{base_url}/{taxi_type}_tripdata_{current:%Y}-{current:%m}.parquet"
    current += relativedelta(months=1)  # move to next month
```

The TLC publishes one `.parquet` file per taxi type per month, e.g.:
```
yellow_tripdata_2022-01.parquet
yellow_tripdata_2022-02.parquet
```
We loop month by month and build the URL for each file.

**Step 3 — Download and read each file**

```python
df = pd.read_parquet(io.BytesIO(requests.get(url).content))
df["taxi_type"]    = taxi_type          # yellow / green
df["extracted_at"] = datetime.utcnow()  # when we fetched it
```

We download the `.parquet` as raw bytes and load it straight into a DataFrame (no saving to disk). We also add two extra columns: `taxi_type` (useful later in staging/reports) and `extracted_at` (for debugging/lineage).

**Step 4 — Return everything**

```python
return pd.concat(frames, ignore_index=True)
```

Stack all the monthly DataFrames into one big DataFrame and return it. Bruin **appends** those rows to `ingestion.trips` in DuckDB.

> **In plain English:** *"For each month in the date window Bruin gave me, download the NYC taxi file for that month, add a couple of extra columns, and hand all the data back to Bruin to store."*

#### Seed asset: `payment_lookup.asset.yml`

The second ingestion asset is a **seed file** — a small, static reference table loaded from a CSV that lives in the repo. The two files work as a pair:

**`payment_lookup.csv`** — the actual data, written by hand:
```csv
payment_type_id,payment_type_name
1,credit_card
2,cash
3,no_charge
4,dispute
```

**`payment_lookup.asset.yml`** — tells Bruin how to load it:
```yaml
name: ingestion.payment_lookup
type: duckdb.seed
parameters:
  path: payment_lookup.csv
columns:
  - name: payment_type_id
    type: integer
    primary_key: true
    checks: [not_null, unique]
  - name: payment_type_name
    type: string
    checks: [not_null]
```

**Why do we need this?** The TLC trip data only gives us a numeric code (`payment_type = 1`, `2`...). The meaning of those numbers isn't in the data — TLC documents them separately. So we create this lookup table and load it into DuckDB so the staging layer can JOIN it:

```
TLC parquet file                  payment_lookup table
-------------------               ----------------------
payment_type = 1    →  JOIN  →    payment_type_name = "credit_card"
payment_type = 2    →  JOIN  →    payment_type_name = "cash"
```

Without it, we'd just have meaningless numbers in our final tables. Why a lookup table instead of a `CASE` statement in SQL? It's easier to maintain (just update the CSV), reusable across multiple assets, and Bruin validates it with quality checks on load.

#### Running the seed asset

```bash
bruin run \
  --start-date 2022-01-01T00:00:00.000Z \
  --end-date 2022-01-30T23:59:59.999999999Z \
  --environment default \
  "05_data-platforms/my-taxi-pipeline/pipeline/assets/ingestion/payment_lookup.asset.yml"
```

Output:
```
✓ Successfully validated 2 assets across 1 pipeline, all good.

[10:39:14] Running:  ingestion.payment_lookup
[10:39:14] >>   Source: csv / seed.raw
[10:39:14] >>   Destination: duckdb / ingestion.payment_lookup
[10:39:14] >>   Incremental Strategy: replace
[10:39:14] >>   Primary Key: ['payment_type_id']
[10:39:14] >> Successfully finished loading data from 'csv' to 'duckdb' in 0.41 seconds
[10:39:15] Finished: ingestion.payment_lookup (5.64s)
[10:39:15] Running:  ingestion.payment_lookup:payment_type_name:not_null
[10:39:15] Running:  ingestion.payment_lookup:payment_type_id:not_null
[10:39:15] Running:  ingestion.payment_lookup:payment_type_id:unique
[10:39:15] Finished: ingestion.payment_lookup:payment_type_name:not_null (80ms)
[10:39:15] Finished: ingestion.payment_lookup:payment_type_id:not_null (150ms)
[10:39:15] Finished: ingestion.payment_lookup:payment_type_id:unique (296ms)

PASS ingestion.payment_lookup ...

bruin run completed successfully in 5.937s
 ✓ Assets executed      1 succeeded
 ✓ Quality checks       3 succeeded
```

After loading the 7 rows from the CSV, Bruin automatically ran **3 quality checks** defined in the asset (not_null on both columns + unique on the ID). All passed. ✅

#### Testing the ingestion asset (one month)

Before building the rest of the pipeline, we test just the ingestion asset with a single month of data:

```bash
bruin run 05_data-platforms/my-taxi-pipeline/pipeline/assets/ingestion/trips.py \
  --environment default \
  --start-date 2022-01-01 \
  --end-date 2022-01-31
```

> **Note:** Run this from the **git root** (`/workspaces/data-engineering-zoomcamp`), not from inside the asset folder. Bruin needs to find `.bruin.yml` at the git root.

Expected output:
```
✓ Successfully validated 1 assets across 1 pipeline, all good.

Interval: 2022-01-01T00:00:00Z - 2022-01-31T00:00:00Z

[09:16:06] >> Fetching: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.parquet
[09:16:11] >>   ✓ 2,463,931 rows loaded
[09:17:06] Finished: ingestion.trips (1m7.764s)

PASS ingestion.trips

bruin run completed successfully in 1m7.765s
 ✓ Assets executed      1 succeeded
```

Verify the data:

```bash
bruin query --connection duckdb-default --query "SELECT COUNT(*) FROM ingestion.trips"
```

```
┌──────────────┐
│ COUNT_STAR() │
├──────────────┤
│ 2463931      │
└──────────────┘
```

**2,463,931 rows** from January 2022 loaded into `ingestion.trips` in DuckDB. ✅

### Staging Layer

The staging layer has one asset: **`staging/trips.sql`** — a SQL asset that reads from both ingestion tables, cleans and enriches the data, and writes to `staging.trips`.

#### Bruin header (`trips.sql`)

```yaml
name: staging.trips
type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: time_interval
  incremental_key: pickup_datetime
  time_granularity: timestamp

custom_checks:
  - name: row_count_positive
    description: Ensures the table is not empty
    query: SELECT COUNT(*) > 0 FROM staging.trips
    value: 1
```

Key points:

| Field | Value | Why |
|-------|-------|-----|
| `depends` | `ingestion.trips`, `ingestion.payment_lookup` | Tells Bruin to run ingestion first; also powers the lineage graph |
| `strategy: time_interval` | — | On each run Bruin **deletes** rows in the time window, then **inserts** the query result — safe reprocessing |
| `incremental_key: pickup_datetime` | — | The column Bruin uses to identify which rows belong to the current window |
| `custom_checks` | `COUNT(*) > 0` → must equal `1` | Ensures staging didn't produce an empty table |

#### Why `time_interval` and not `append`?

The ingestion layer uses `append` (raw data accumulates). The staging layer uses `time_interval` so we can safely **reprocess** any time window without duplicating rows — perfect for backfilling or re-running a broken day.

#### The SELECT query — 4 staging rules

The template comments list 4 things every staging asset should do:

```sql
SELECT
    t.pickup_datetime,
    t.dropoff_datetime,
    t.pu_location_id,
    t.do_location_id,
    t.passenger_count,
    t.trip_distance,
    t.fare_amount,
    t.tip_amount,
    t.total_amount,
    p.payment_type_name,   -- (3) enriched from lookup
    t.taxi_type,
    t.extracted_at

FROM ingestion.trips t
LEFT JOIN ingestion.payment_lookup p   -- (3) enrich with JOIN
    ON t.payment_type = p.payment_type_id

WHERE
    t.pickup_datetime >= '{{ start_datetime }}'  -- (1) time window filter
    AND t.pickup_datetime < '{{ end_datetime }}'
    AND t.pickup_datetime IS NOT NULL             -- (4) drop invalid rows
    AND t.fare_amount >= 0

QUALIFY ROW_NUMBER() OVER (                       -- (2) deduplicate
    PARTITION BY t.pickup_datetime, t.dropoff_datetime,
                 t.pu_location_id, t.do_location_id,
                 t.fare_amount, t.taxi_type
    ORDER BY t.extracted_at DESC
) = 1
```

| Rule | Technique | Reason |
|------|-----------|--------|
| 1. Filter to time window | `WHERE pickup_datetime >= '{{ start_datetime }}'` | Required by `time_interval` — without it you'd insert all data but only delete the window → duplicates |
| 2. Deduplicate | `QUALIFY ROW_NUMBER() = 1` | Ingestion uses `append`, so re-runs can land the same trip twice; keep the latest copy |
| 3. Enrich with JOINs | `LEFT JOIN ingestion.payment_lookup` | Replaces `payment_type = 1` with `payment_type_name = "credit_card"` |
| 4. Filter invalid rows | `IS NOT NULL`, `fare_amount >= 0` | Drop rows that can't be used in reports |


#### Running the staging asset

```bash
bruin run 05_data-platforms/my-taxi-pipeline/pipeline/assets/staging/trips.sql \
  --environment default \
  --start-date 2022-01-01 \
  --end-date 2022-01-31 \
  --full-refresh
```

```
PASS staging.trips

bruin run completed successfully in 4.983s
 ✓ Assets executed      1 succeeded
 ✓ Quality checks       1 succeeded
```

#### Gotchas we hit

**1. First run fails without `--full-refresh`**

```
Catalog Error: Table with name trips does not exist!
LINE 2: DELETE FROM staging.trips WHERE pickup_datetime BETWEEN ...
```

The `time_interval` strategy always tries to **DELETE** rows from the table before inserting — but `staging.trips` doesn't exist on the very first run. Fix: pass `--full-refresh` on the first run. It skips the DELETE and does a clean `CREATE TABLE AS SELECT` instead. Subsequent runs work normally without the flag.

**2. Wrong column names — TLC uses `tpep_` prefix**

```
Binder Error: Table "t" does not have a column named "pickup_datetime"
Candidate bindings: "tpep_pickup_datetime"
```

The yellow taxi TLC parquet files use `tpep_pickup_datetime` / `tpep_dropoff_datetime` (tpep = Taxicab Passenger Enhancement Program), not plain `pickup_datetime`. We discovered the real column names by querying the schema:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'trips' AND table_schema = 'ingestion'
ORDER BY ordinal_position;
```

Fix: replace all references to `pickup_datetime` / `dropoff_datetime` with `tpep_pickup_datetime` / `tpep_dropoff_datetime` — including the `incremental_key` in the Bruin header.

### Reports Layer

The reports layer (`pipeline/assets/reports/trips_report.sql`) aggregates the clean, deduplicated staging data into a **dashboard-ready summary table**. Here is a section-by-section breakdown.

#### `name` & `type`

```yaml
name: reports.trips_report
type: duckdb.sql
```

- **`name`** — defines the asset's identifier in the Bruin DAG. The `reports.` prefix maps to the `reports` schema in DuckDB, and `trips_report` becomes the table name.
- **`type: duckdb.sql`** — tells Bruin this is a SQL asset that runs against DuckDB.

#### `depends`

```yaml
depends:
  - staging.trips
```

Bruin uses this to ensure `staging.trips` is fully built and tested **before** this asset runs. It also determines the correct execution order in the pipeline DAG automatically.

#### `materialization`

```yaml
materialization:
  type: table
  strategy: time_interval
  incremental_key: trip_date
  time_granularity: date
```

- **`type: table`** — Bruin will `CREATE OR REPLACE` a persistent table (not a view).
- **`strategy: time_interval`** — instead of rebuilding the whole table every run, Bruin **deletes** the rows in the current time window and **re-inserts** them. This makes backfills efficient.
- **`incremental_key: trip_date`** — the column Bruin uses to determine which rows belong to the current time window. Our SELECT produces `trip_date` (a DATE from `CAST(tpep_pickup_datetime AS DATE)`), so Bruin can slice the table by it.
- **`time_granularity: date`** — tells Bruin the key is at DATE precision (vs. `timestamp`). The staging layer used `tpep_pickup_datetime` (a timestamp) as its incremental key, but here we've aggregated down to a date so we switch granularity.

#### `columns` — Primary Keys & Quality Checks

The report has **3 primary keys** — the combination of `trip_date + taxi_type + payment_type_name` uniquely identifies each row (one row per day, taxi type, and payment method):

```yaml
columns:
  - name: trip_date          # primary_key: true
  - name: taxi_type          # primary_key: true
  - name: payment_type_name  # primary_key: true
  - name: trip_count
    checks:
      - name: positive        # must be > 0
  - name: total_passengers / total_distance / total_fare / total_tips / total_revenue
    checks:
      - name: non_negative    # must be >= 0
  - name: avg_fare / avg_trip_distance / avg_passengers
    # no check — if sums pass, averages are implicitly valid
```

- **`positive` on `trip_count`** — must be **> 0**. Every group must have at least one trip; a zero here would indicate a pipeline bug.
- **`non_negative` on totals** — must be **≥ 0**. Slightly looser than `positive` because a group could theoretically have a $0 total.
- **No check on averages** — derived metrics; if the sum checks pass, averages are implicitly valid.

#### SQL Query Logic

```sql
SELECT
    CAST(tpep_pickup_datetime AS DATE)      AS trip_date,
    COALESCE(taxi_type, 'Unknown')          AS taxi_type,
    COALESCE(payment_type_name, 'Unknown')  AS payment_type_name,
    COUNT(*)                                AS trip_count,
    SUM(passenger_count)                    AS total_passengers,
    ROUND(SUM(trip_distance), 2)            AS total_distance,
    ROUND(SUM(fare_amount), 2)              AS total_fare,
    ROUND(SUM(tip_amount), 2)               AS total_tips,
    ROUND(SUM(total_amount), 2)             AS total_revenue,
    ROUND(AVG(fare_amount), 4)              AS avg_fare,
    ROUND(AVG(trip_distance), 4)            AS avg_trip_distance,
    ROUND(AVG(passenger_count), 4)          AS avg_passengers
FROM staging.trips
WHERE tpep_pickup_datetime >= '{{ start_datetime }}'
  AND tpep_pickup_datetime <  '{{ end_datetime }}'
GROUP BY
    CAST(tpep_pickup_datetime AS DATE),
    COALESCE(taxi_type, 'Unknown'),
    COALESCE(payment_type_name, 'Unknown')
```

| Part | Purpose |
|---|---|
| `CAST(... AS DATE)` | Truncates timestamp → date for daily aggregation |
| `COALESCE(..., 'Unknown')` | Handles NULLs so they don't silently disappear from `GROUP BY` |
| `{{ start_datetime }}` / `{{ end_datetime }}` | Bruin injects these at runtime based on the scheduled / backfill window |
| `WHERE` on `tpep_pickup_datetime` | Filters staging data to this run's time window **before** grouping |
| `GROUP BY` | Collapses all trips for a (date, taxi type, payment method) into one row |
| `ROUND(..., 2)` on totals | Keeps money/distance to 2 decimal places |
| `ROUND(..., 4)` on averages | Keeps averages slightly more precise |

> **Pipeline flow summary**: raw ingestion → staging (deduplicated, enriched, validated) → **reports** (aggregated, dashboard-ready). This is the table a BI tool would query.

### Running the Pipeline

> Clarifications will be added here as we go through the video.

