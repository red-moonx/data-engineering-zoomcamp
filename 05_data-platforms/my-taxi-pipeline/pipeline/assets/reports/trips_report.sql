/* @bruin

name: reports.trips_report
type: duckdb.sql

depends:
  - staging.trips

materialization:
  type: table
  strategy: time_interval
  incremental_key: trip_date
  time_granularity: date

columns:
  - name: trip_date
    type: DATE
    description: Date of the trip (based on pickup_datetime)
    primary_key: true
  - name: taxi_type
    type: VARCHAR
    description: Type of taxi (yellow, green)
    primary_key: true
  - name: payment_type_name
    type: VARCHAR
    description: Payment method name (credit card, cash, etc.)
    primary_key: true
  - name: trip_count
    type: BIGINT
    description: Total number of trips
    checks:
      - name: positive
  - name: total_passengers
    type: BIGINT
    description: Total number of passengers
    checks:
      - name: non_negative
  - name: total_distance
    type: DOUBLE
    description: Total trip distance in miles
    checks:
      - name: non_negative
  - name: total_fare
    type: DOUBLE
    description: Total fare amount
    checks:
      - name: non_negative
  - name: total_tips
    type: DOUBLE
    description: Total tips collected
    checks:
      - name: non_negative
  - name: total_revenue
    type: DOUBLE
    description: Total revenue (total_amount)
    checks:
      - name: non_negative
  - name: avg_fare
    type: DOUBLE
    description: Average fare per trip
  - name: avg_trip_distance
    type: DOUBLE
    description: Average trip distance in miles
  - name: avg_passengers
    type: DOUBLE
    description: Average passengers per trip

@bruin */

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

ORDER BY
    trip_date,
    taxi_type,
    payment_type_name
