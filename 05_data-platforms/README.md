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

### Ingestion Layer

> Clarifications will be added here as we go through the video.

### Staging Layer

> Clarifications will be added here as we go through the video.

### Reports Layer

> Clarifications will be added here as we go through the video.

### Running the Pipeline

> Clarifications will be added here as we go through the video.

