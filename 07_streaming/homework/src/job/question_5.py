import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

def run_session_job():
    """
    Question 5: Session window - longest streak.
    5-minute gap session window on PULocationID.
    Saves results to PostgreSQL.
    """
    # 1. Setup Execution Environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # 2. Source DDL
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
            'properties.group.id' = 'flink-question-5',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """
    t_env.execute_sql(src_ddl)

    # 3. Sink DDL
    sink_ddl = """
        CREATE TABLE processed_session_counts (
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            PULocationID INTEGER,
            num_trips BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'processed_session_counts',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        )
    """
    t_env.execute_sql(sink_ddl)

    # 4. Aggregation Query (Session Window with 5 Minute Gap)
    query = """
        INSERT INTO processed_session_counts
        SELECT 
            SESSION_START(event_timestamp, INTERVAL '5' MINUTE) AS window_start,
            SESSION_END(event_timestamp, INTERVAL '5' MINUTE) AS window_end,
            PULocationID,
            COUNT(*) AS num_trips
        FROM green_trips
        GROUP BY 
            SESSION(event_timestamp, INTERVAL '5' MINUTE),
            PULocationID
    """
    print("Submitting Session Window Job (Question 5) to Flink...")
    t_env.execute_sql(query).wait()

if __name__ == '__main__':
    run_session_job()
