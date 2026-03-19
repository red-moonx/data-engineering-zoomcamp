import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

def run_window_job():
    """
    Question 4: Tumbling window - pickup location.
    5-minute tumbling window counting trips per PULocationID.
    Saves result to PostgreSQL.
    """
    # 1. Setup Execution Environment
    env = StreamExecutionEnvironment.get_execution_environment()
    # Task requirement: set parallelism to 1 because topic has 1 partition
    env.set_parallelism(1)
    
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # 2. Source DDL: Kafka/Redpanda
    # Note: Using 'redpanda:29092' for internal docker communication
    # and TO_TIMESTAMP for string-to-time conversion.
    src_ddl = """
        CREATE TABLE green_trips (
            lpep_pickup_datetime STRING,
            PULocationID INTEGER,
            event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'properties.group.id' = 'flink-question-4',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(src_ddl)

    # 3. Sink DDL: PostgreSQL
    # Using 'postgres:5432' for internal docker communication
    sink_ddl = """
        CREATE TABLE processed_pulocation_counts (
            window_start TIMESTAMP(3),
            PULocationID INTEGER,
            num_trips BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'processed_pulocation_counts',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)

    # 4. Aggregation Query (Tumbling Window of 5 Minutes)
    query = """
        INSERT INTO processed_pulocation_counts
        SELECT 
            TUMBLE_START(event_timestamp, INTERVAL '5' MINUTE) AS window_start,
            PULocationID,
            COUNT(*) AS num_trips
        FROM green_trips
        GROUP BY 
            TUMBLE(event_timestamp, INTERVAL '5' MINUTE),
            PULocationID
    """
    print("Submitting Windowing Job (Question 4) to Flink...")
    t_env.execute_sql(query).wait()

if __name__ == '__main__':
    run_window_job()
