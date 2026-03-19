import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

def run_tip_job():
    """
    Question 6: Tumbling window - largest tip.
    1-hour tumbling window computing total tip_amount per hour (across all locations).
    Saves result to PostgreSQL.
    """
    # 1. Setup Execution Environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # 2. Source DDL: Redpanda
    src_ddl = """
        CREATE TABLE green_trips (
            lpep_pickup_datetime STRING,
            tip_amount DOUBLE,
            event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'properties.group.id' = 'flink-question-6',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(src_ddl)

    # 3. Sink DDL: PostgreSQL
    sink_ddl = """
        CREATE TABLE processed_hourly_tips (
            window_start TIMESTAMP(3),
            total_tip DOUBLE
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'processed_hourly_tips',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)

    # 4. Aggregation Query (1-Hour Tumbling Window)
    # We remove PULocationID to aggregate for all locations.
    query = """
        INSERT INTO processed_hourly_tips
        SELECT 
            TUMBLE_START(event_timestamp, INTERVAL '1' HOUR) AS window_start,
            SUM(tip_amount) AS total_tip
        FROM green_trips
        GROUP BY 
            TUMBLE(event_timestamp, INTERVAL '1' HOUR)
    """
    print("Submitting Hourly Tip Job (Question 6) to Flink...")
    t_env.execute_sql(query).wait()

if __name__ == '__main__':
    run_tip_job()
