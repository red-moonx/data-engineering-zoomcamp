# Progress Report: Data Engineering Zoomcamp Homework Assistance

This document summarizes all the technical steps and modifications performed by Antigravity to assist in solving the Module 1 Homework.

## 1. Initial Exploration and Setup
- Navigated to the project directory: `/workspaces/data-engineering-zoomcamp/01_docker-and-terraform/homework`.
- Confirmed the presence of `homework_with_answers.md` and initial environment files.

## 2. Theoretical Clarification (Question 2)
- Explained Docker Compose networking and service discovery.
- Defined why `db:5432` is the correct connection string for internal container communication (pgAdmin to Postgres) versus `localhost:5433` for external host communication.

## 3. Data Preparation
- Downloaded the required datasets using `wget`:
  - Green Taxi Trip Data (Nov 2025): `green_tripdata_2025-11.parquet`
  - Taxi Zone Lookup: `taxi_zone_lookup.csv`

## 4. Environment and Dependency Management
- **`pyproject.toml` Updates**: Added essential libraries for the ingestion script:
  - `click` (CLI support)
  - `sqlalchemy` (Database ORM)
  - `psycopg2-binary` (Postgres driver)
  - `tqdm` (Progress bars)
- **Lockfile Synchronization**: Ran `uv lock` to update `uv.lock` with the specific versions of the new dependencies.

## 5. Ingestion Script Refinement (`ingest_data.py`)
Modified the provided Yellow Taxi script to support the specific homework requirements:
- **Parquet Support**: Integrated `pandas.read_parquet` to handle the `.parquet` format.
- **Improved Versatility**: Replaced hardcoded URLs/logic with a `--file-path` argument, allowing the script to ingest any local file (Parquet or CSV).
- **Date Handling**: Added logic to automatically detect and convert datetime columns for Green taxi data (`lpep_pickup_datetime`).
- **Chunking Logic**: Maintained the iterator pattern for CSV files while allowing full loads for smaller Parquet files.

## 6. Docker Infrastructure
- **`Dockerfile`**: Created a multi-stage Dockerfile utilizing `uv` for fast, reproducible builds of the ingestion tool.
- **`docker-compose.yaml`**: Orchestrated two services:
  - `pgdatabase`: Postgres 18.
  - `pgadmin`: Web-based database management.
- **Troubleshooting**: Identified and fixed a Postgres 18-specific volume mount error (ensuring the volume maps to `/var/lib/postgresql` instead of the legacy `/var/lib/postgresql/data`).

## 7. Data Ingestion Execution
- Built the `taxi_ingest:v001` Docker image.
- Successfully ran the ingestion container twice:
  - **Green Trips**: Loaded 46,912 records into the `green_tripdata` table.
  - **Zones**: Loaded the zone lookup table into the `zones` table.

## 8. Homework Analysis and Documentation
- Answered **Questions 3, 4, 5, and 6** using SQL queries executed against the live Postgres database.
- Answered **Question 7** based on Terraform workflow principles (`init`, `apply`, `destroy`).
- Updated `homework_with_answers.md` by appending "MY ANSWER" sections with the specific SQL queries and results while strictly preserving the teacher's original options.

---
**Report generated on:** 2026-01-26
