# Module 5 — Handoff Note
_Last saved: 2026-02-28 ~11:49 UTC_

## Where we left off

We are following the Bruin NYC Taxi pipeline course (Module 5). Here is the current state:

### ✅ Done
- **`pipeline.yml`** — configured (name, schedule, start_date, connections, variables)
- **`ingestion/trips.py`** — Python asset complete, tested (Jan 2022, 2,463,931 rows loaded)
- **`ingestion/payment_lookup.asset.yml` + `.csv`** — seed asset complete, tested (7 rows, 3 quality checks passed)
- **`ingestion/requirements.txt`** — pinned versions added
- **`staging/trips.sql`** — SQL asset complete, tested (Jan 2022, PASS + custom check passed)
- **README.md** — fully documented: pipeline.yml, ingestion layer (trips.py + seed), staging layer (with gotchas)

### 🔜 Next step: Reports Layer
- `reports/trips_report.sql` is now in place at `pipeline/assets/reports/trips_report.sql`
- Still has TODO placeholders — needs to be completed following the template comments
- After that: run the full pipeline end-to-end and document in the "Running the Pipeline" section of the README

### Key things to know
- **`.bruin.yml` and `duckdb.db` are at the git root** (not in `05_data-platforms/`) — required by Bruin
- **Always run `bruin` from the git root** (`/workspaces/data-engineering-zoomcamp`)
- **First run of a `time_interval` asset needs `--full-refresh`** (table doesn't exist yet)
- **TLC yellow taxi columns** use `tpep_pickup_datetime` / `tpep_dropoff_datetime` (not plain `pickup_datetime`)
- **DuckDB schema query** to inspect columns: `SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'trips' AND table_schema = 'ingestion'`
- **`_todo_assets/`** folder is now empty — all assets have been moved back to their proper locations

### File locations
```
05_data-platforms/my-taxi-pipeline/
├── _todo_assets/          ← empty now, can be deleted
├── pipeline/
│   └── assets/
│       ├── ingestion/
│       │   ├── trips.py
│       │   ├── payment_lookup.asset.yml
│       │   ├── payment_lookup.csv
│       │   └── requirements.txt
│       ├── staging/
│       │   └── trips.sql
│       └── reports/
│           └── trips_report.sql  ← NEXT: fill this in
```
