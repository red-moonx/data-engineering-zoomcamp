# Handoff - Module 7: Streaming Development

## Context
We are working on **Module 7: Streaming**. The environment is fully initialized with `uv` (Python 3.12).

## Current Progress
- **Infrastructure:**
    - Redpanda and PostgreSQL are configured and running in Docker.
    - Flink `Dockerfile`, `config`, and `pyproject` files have been downloaded via `wget`.
- **Database:** `processed_events` table has been created in Postgres via `pgcli`.
- **Connectivity:** `psycopg2-binary` installed to allow Python → Postgres communication.
- **Documentation:** `README.md` is fully updated with deep dives into:
    - Serialization (Object → Dict → JSON → Bytes).
    - Flink vs. Spark (Native vs. Micro-batch).
    - Checkpointing & Fault Tolerance.
    - Watermarks (Patience Fix) and Window types (Tumbling/Sliding/Session).
    - Upsert logic with Primary Keys in Postgres.
    - Infrastructure explanation for the hybrid `Dockerfile.flink`.

## Completed Actions
1. Verified `models.py` logic and documented the "middle-man" dictionary role.
2. Successfully ran `SELECT COUNT(1)` on the database (confirmed 0 rows, ready for data).
3. Prepared the Flink custom image recipe.
4. Comprehensive update to `README.md` merging theory and implementation.

## Next Steps for Later
1. **Build Flink:** Run `docker compose build` to create the custom PyFlink image.
2. **Start Flink:** Run `docker compose up -d` to bring up the JobManager and TaskManager.
3. **Trigger Stream:** Run `producer.ipynb` to start sending taxi events.
4. **Verify Flow:** Run `consumer_db.ipynb` and check the table count again in `pgcli`.
5. **Flink Development:** Transition to `pass_through_job.py` and `aggregation_job.py`.
