/* @bruin

# Docs:
# - Materialization: https://getbruin.com/docs/bruin/assets/materialization
# - Quality checks (built-ins): https://getbruin.com/docs/bruin/quality/available_checks
# - Custom checks: https://getbruin.com/docs/bruin/quality/custom

name: staging.trips
type: duckdb.sql

depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table
  strategy: time_interval
  incremental_key: tpep_pickup_datetime
  time_granularity: timestamp

custom_checks:
  - name: row_count_positive
    description: Ensures the table is not empty
    query: SELECT COUNT(*) > 0 FROM staging.trips
    value: 1

@bruin */

-- Staging layer — following the 4 recommendations from the template comments:
--
-- 1. Filter to the current run's time window (required by time_interval strategy)
-- 2. Deduplicate — ingestion uses append, so the same trip can land multiple times
-- 3. Enrich with lookup table JOIN (replace numeric payment_type with readable name)
-- 4. Filter invalid rows (null pickup_datetime, negative fares)

SELECT
    -- timestamps
    t.tpep_pickup_datetime,
    t.tpep_dropoff_datetime,

    -- locations
    t.pu_location_id,
    t.do_location_id,

    -- trip details
    t.passenger_count,
    t.trip_distance,

    -- financials
    t.fare_amount,
    t.tip_amount,
    t.total_amount,

    -- enriched payment name (recommendation 3: JOIN lookup)
    p.payment_type_name,

    -- lineage columns from ingestion
    t.taxi_type,
    t.extracted_at

FROM ingestion.trips t
LEFT JOIN ingestion.payment_lookup p
    ON t.payment_type = p.payment_type_id

WHERE
    -- recommendation 1: filter to the run's time window
    t.tpep_pickup_datetime >= '{{ start_datetime }}'
    AND t.tpep_pickup_datetime < '{{ end_datetime }}'
    -- recommendation 4: drop rows with null primary key or negative fares
    AND t.tpep_pickup_datetime IS NOT NULL
    AND t.fare_amount >= 0

-- recommendation 2: deduplicate (keep one row per trip)
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY t.tpep_pickup_datetime, t.tpep_dropoff_datetime,
                 t.pu_location_id, t.do_location_id,
                 t.fare_amount, t.taxi_type
    ORDER BY t.extracted_at DESC
) = 1
