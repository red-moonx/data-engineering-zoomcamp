# Module 5 Homework: Data Platforms with Bruin

---

### Question 1. Bruin Pipeline Structure

**In a Bruin project, what are the required files/directories?**

- `bruin.yml` and `assets/`
- `.bruin.yml` and `pipeline.yml` (assets can be anywhere)
- `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`
- `pipeline.yml` and `assets/` only

> [!TIP]
> **My Answer:** `.bruin.yml` and `pipeline/` with `pipeline.yml` and `assets/`
>
> According to the [Bruin docs](https://getbruin.com/docs/bruin/getting-started/pipeline), a pipeline is defined with a `pipeline.yml` file, and all assets **must be under a folder called `assets/` next to it**:
> ```
> my-pipeline/
> ├─ pipeline.yml
> └─ assets/
>     ├─ ingestion/
>     ├─ staging/
>     └─ reports/
> ```
> `.bruin.yml` lives at the **workspace root** and holds environment/connection definitions (gitignored — contains credentials). Assets can be organized into subdirectories inside `assets/`, but the `assets/` folder itself is required next to `pipeline.yml`.

---

### Question 2. Materialization Strategies

**You're building a pipeline that processes NYC taxi data organized by month based on `pickup_datetime`. Which incremental strategy is best for processing a specific interval period by deleting and inserting data for that time period?**

- `append` - always add new rows
- `replace` - truncate and rebuild entirely
- `time_interval` - incremental based on a time column
- `view` - create a virtual table only

> [!TIP]
> **My Answer:** `time_interval` — incremental based on a time column
>
> `time_interval` is exactly the strategy we used in both `staging.trips` and `reports.trips_report`. On each run, Bruin **deletes** the rows inside the current date window (using the `incremental_key` column) and then **re-inserts** the query result for that window. This makes backfilling and reprocessing safe and idempotent — running the same window twice will not produce duplicates.

---

### Question 3. Pipeline Variables

**You have the following variable defined in `pipeline.yml`:**

```yaml
variables:
  taxi_types:
    type: array
    items:
      type: string
    default: ["yellow", "green"]
```

**How do you override this when running the pipeline to only process yellow taxis?**

- `bruin run --taxi-types yellow`
- `bruin run --var taxi_types=yellow`
- `bruin run --var 'taxi_types=["yellow"]'`
- `bruin run --set taxi_types=["yellow"]`

> [!TIP]
> **My Answer:** `bruin run --var 'taxi_types=["yellow"]'`
>
> The `--var` flag is the correct way to override pipeline variables at runtime. Since `taxi_types` is defined as an **array**, the value must be passed as a JSON array string: `'taxi_types=["yellow"]'`. 

---

### Question 4. Running with Dependencies

**You've modified the `ingestion/trips.py` asset and want to run it plus all downstream assets. Which command should you use?**

- `bruin run ingestion.trips --all`
- `bruin run ingestion/trips.py --downstream`
- `bruin run pipeline/trips.py --recursive`
- `bruin run --select ingestion.trips+`

> [!TIP]
> **My Answer:** `bruin run ingestion/trips.py --downstream`
>
> The `--downstream` flag tells Bruin to run the specified asset **and all assets that depend on it**, following the lineage graph automatically. In our pipeline, running `ingestion/trips.py --downstream` would also trigger `staging.trips` and then `reports.trips_report` in the correct order.

---

### Question 5. Quality Checks

**You want to ensure the `pickup_datetime` column in your trips table never has NULL values. Which quality check should you add to your asset definition?**

- `name: unique`
- `name: not_null`
- `name: positive`
- `name: accepted_values, value: [not_null]`

> [!TIP]
> **My Answer:** `name: not_null`
>
> The `not_null` check is a built-in Bruin quality check that verifies every value in the specified column is non-null. 

---

### Question 6. Lineage and Dependencies

**After building your pipeline, you want to visualize the dependency graph between assets. Which Bruin command should you use?**

- `bruin graph`
- `bruin dependencies`
- `bruin lineage`
- `bruin show`

> [!TIP]
> **My Answer:** `bruin lineage`
>
> `bruin lineage` dumps the upstream and downstream dependency graph for a given asset. For example:


---

### Question 7. First-Time Run

**You're running a Bruin pipeline for the first time on a new DuckDB database. What flag should you use to ensure tables are created from scratch?**

- `--create`
- `--init`
- `--full-refresh`
- `--truncate`

> [!TIP]
> **My Answer:** `--full-refresh`
>
> We hit this exact issue during development! The `time_interval` materialization strategy tries to **DELETE** rows from the target table before inserting — but on the first run, the table doesn't exist yet and the DELETE fails:
> ```
> Catalog Error: Table with name trips does not exist!
> LINE 2: DELETE FROM staging.trips WHERE pickup_datetime BETWEEN ...
> ```
> Passing `--full-refresh` skips the DELETE and instead does a clean `CREATE TABLE AS SELECT`, creating the table from scratch. Subsequent runs work normally without the flag.
