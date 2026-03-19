# Homework

In this homework, we'll practice streaming with Kafka (Redpanda) and PyFlink.

We use Redpanda, a drop-in replacement for Kafka. It implements the same
protocol, so any Kafka client library works with it unchanged.

For this homework we will be using Green Taxi Trip data from October 2025:

- [green_tripdata_2025-10.parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet)


## Setup

We have used the same infrastructure from the [workshop](../../07_streaming/docker-compose.yml).

Follow the setup instructions: build the Docker image, start the services:


> [!TIP]
> **My Answer:**
> To get started, I downloaded the taxi trip data for October 2025 and launched the streaming infrastructure.
>
> **Steps taken:**
> 1. Downloaded the dataset:
> ```bash
> wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet
> ```
> 2. Started the Docker stack (Redpanda, Flink, and Postgres) using the workshop configuration in the parent directory:
> ```bash
> docker compose -f ../docker-compose.yml up -d
> ```

This gives us:

- Redpanda (Kafka-compatible broker) on `localhost:9092`
- Flink Job Manager at http://localhost:8081
- Flink Task Manager
- PostgreSQL on `localhost:5432` (user: `postgres`, password: `postgres`)

If you previously ran the workshop and have old containers/volumes,
do a clean start:

```bash
docker compose down -v
docker compose build
docker compose up -d
```

Note: the container names (like `workshop-redpanda-1`) assume the
directory is called `workshop`. If you renamed it, adjust accordingly.


## Question 1. Redpanda version

Run `rpk version` inside the Redpanda container:

```bash
docker exec -it 07_streaming-redpanda-1 rpk version
```

What version of Redpanda are you running?

> [!TIP]
> **My Answer:**
> Instead of manually entering the container, I used `docker exec` to run the version command directly from the host.
>
> **Steps taken:**
> I ran the following command to query the Redpanda version directly:
> ```bash
> docker exec -it 07_streaming-redpanda-1 rpk version
> ```
> 
> **Output:**
> ```text
> rpk version: v25.3.9
> Git ref:     836b4a36ef6d5121edbb1e68f0f673c2a8a244e2
> Build date:  2026 Feb 26 07 48 21 Thu
> OS/Arch:     linux/amd64
> Go version:  go1.24.3
> ```
> The version is **v25.3.9**.

## Question 2. Sending data to Redpanda

Create a topic called `green-trips`:

```bash
docker exec -it workshop-redpanda-1 rpk topic create green-trips
```

Now write a producer to send the green taxi data to this topic.

Read the parquet file and keep only these columns:

- `lpep_pickup_datetime`
- `lpep_dropoff_datetime`
- `PULocationID`
- `DOLocationID`
- `passenger_count`
- `trip_distance`
- `tip_amount`
- `total_amount`

Convert each row to a dictionary and send it to the `green-trips` topic.
You'll need to handle the datetime columns - convert them to strings
before serializing to JSON.

Measure the time it takes to send the entire dataset and flush:

```python
from time import time

t0 = time()

# send all rows ...

producer.flush()

t1 = time()
print(f'took {(t1 - t0):.2f} seconds')
```

How long did it take to send the data?

- 10 seconds
- 60 seconds
- 120 seconds
- 300 seconds

> [!TIP]
> **My Answer:**
> I created a Python producer script [producer_green.py](producer_green.py) to automate the entire data ingestion process.
>
> **Script Architecture:**
> - **1. Topic Creation**: Uses `KafkaAdminClient` to check for and create the `green-trips` topic with 1 partition (essential for Flink watermarks later).
> - **2. Data Loading & Cleaning**: Reads the October 2025 Green Taxi Parquet file using `pandas`, keeping only the 8 required columns.
> - **3. Datetime Transformation**: Converts binary pickup/dropoff timestamps into standard strings (`YYYY-MM-DD HH:MM:SS`) before JSON serialization.
> - **4. Measurement & Ingestion**: Uses a `KafkaProducer` to send all records and includes a `flush()` call to ensure the stopwatch captures the total network transit time.
>
> **Steps taken:**
> I executed the ingestion using the following command:
> ```bash
> uv run python producer_green.py
> ```
> 
> **Output:**
> ```text
> Topic green-trips already exists.
> Reading data from green_tripdata_2025-10.parquet...
> Starting to send 49416 records...
> Sending took 10.07 seconds
> ```
> The ingestion took approximately **10.07 seconds** (which falls into the **10 seconds** category). We measured the time from the start of the ingestion loop until the `flush()` command ensured all buffered records were definitively sent to the Redpanda broker.

## Question 3. Consumer - trip distance

Write a Kafka consumer that reads all messages from the `green-trips` topic
(set `auto_offset_reset='earliest'`).

Count how many trips have a `trip_distance` greater than 5.0 kilometers.

How many trips have `trip_distance` > 5?

- 6506
- 7506
- 8506
- 9506

> [!TIP]
> **My Answer:**
> I created a consumer script [consumer_green.py](consumer_green.py) to process the records and count those meeting the distance criteria.
>
> **Execution Output:**
> ```text
> ========================================
>       KAFKA CONSUMER REPORT
> ========================================
> Total messages processed: 49416
> Trips with distance > 5.0: 8506
> ========================================
> End of processing.
> ```
> There are **8,506** trips with a distance greater than 5.0 kilometers.

For the PyFlink questions, you'll adapt the workshop code to work with
the green taxi data. The key differences from the workshop:

- Topic name: `green-trips` (instead of `rides`)
- Datetime columns use `lpep_` prefix (instead of `tpep_`)
- You'll need to handle timestamps as strings (not epoch milliseconds)

You can convert string timestamps to Flink timestamps in your source DDL:

```sql
lpep_pickup_datetime VARCHAR,
event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
```

Before running the Flink jobs, create the necessary PostgreSQL tables
for your results.

Important notes for the Flink jobs:

- Place your job files in `workshop/src/job/` - this directory is
  mounted into the Flink containers at `/opt/src/job/`
- Submit jobs with:
  `docker exec -it workshop-jobmanager-1 flink run -py /opt/src/job/your_job.py`
- The `green-trips` topic has 1 partition, so set parallelism to 1
  in your Flink jobs (`env.set_parallelism(1)`). With higher parallelism,
  idle consumer subtasks prevent the watermark from advancing.
- Flink streaming jobs run continuously. Let the job run for a minute
  or two until results appear in PostgreSQL, then query the results.
  You can cancel the job from the Flink UI at http://localhost:8081
- If you sent data to the topic multiple times, delete and recreate
  the topic to avoid duplicates:
  `docker exec -it workshop-redpanda-1 rpk topic delete green-trips`

### Homework project structure

I have restructured the directory as a fully independent project (to avoid configuration clashes with the workshop materials).

```text
07_streaming/homework/
├── docker-compose.yml           # Redpanda, Postgres, and Flink infrastructure
├── pyflink-custom.Dockerfile    # Docker image definition for Flink with local dependencies
├── src/                         # Organized source code
│   ├── producers/
│   │   └── producer_green.py    # Python producer (using Dataclasses and NaN handling)
│   ├── consumers/
│   │   └── consumer_green.py    # Python consumer for basic data validation
│   └── job/
│       └── question_4.py        # PyFlink streaming job (Tumbling Window counting)
└── README.md                    # This documentation
```

Key features of this setup:
*   **Independent Project**: `docker compose up` inside this folder generates containers prefixed with `homework-`.
*   **Source Mounting**: The local `./src` folder is mounted to `/opt/src` inside the Flink jobmanager and taskmanager containers.

## Question 4. Tumbling window - pickup location

Create a Flink job that reads from `green-trips` and uses a 5-minute
tumbling window to count trips per `PULocationID`.

Write the results to a PostgreSQL table with columns:
`window_start`, `PULocationID`, `num_trips`.

After the job processes all data, query the results:

```sql
SELECT PULocationID, num_trips
FROM <your_table>
ORDER BY num_trips DESC
LIMIT 3;
```

Which `PULocationID` had the most trips in a single 5-minute window?

- 42
- 74
- 75
- 166

> [!TIP]
> **My Answer:**
> To solve this, I first initialized the results table in PostgreSQL and then submitted the PyFlink job.
>
> **Step 1: Create the Sink Table**
> We create the target table in our dedicated homework Postgres container:
> ```bash
> docker exec -it homework-postgres-1 psql -U postgres -d postgres -c "
> CREATE TABLE IF NOT EXISTS processed_pulocation_counts (
>     window_start TIMESTAMP,
>     PULocationID INTEGER,
>     num_trips BIGINT
> );"
> ```
> 
> **Step 2: Submit the Flink Job**
> Run the windowing job (Question 4) from the jobmanager:
> ```bash
> docker exec -it homework-jobmanager-1 flink run -py /opt/src/job/question_4.py
> ```
> 
> **Step 3: Query the Results**
> After the job has processed the records, I run the following query:
> ```sql
> docker exec -it homework-postgres-1 psql -U postgres -d postgres -c "
> SELECT PULocationID, num_trips, window_start
> FROM processed_pulocation_counts
> ORDER BY num_trips DESC
> LIMIT 3;"
> ```
> **Output:**
> ```text
>  pulocationid | num_trips |    window_start     
> --------------+-----------+---------------------
>            74 |        15 | 2025-10-22 08:40:00
>            74 |        14 | 2025-10-20 16:30:00
>            74 |        13 | 2025-10-08 10:35:00
> (3 rows)
> ```
> The answer is **74**.
>
> Essentially, this query answers the question: Which part of the city was the busiest at its absolute busiest moment (any single 5-minute period)?"
> 

## Question 5. Session window - longest streak

Create another Flink job that uses a session window with a 5-minute gap
on `PULocationID`, using `lpep_pickup_datetime` as the event time
with a 5-second watermark tolerance.

A session window groups events that arrive within 5 minutes of each other.
When there's a gap of more than 5 minutes, the window closes.

Write the results to a PostgreSQL table and find the `PULocationID`
with the longest session (most trips in a single session).

How many trips were in the longest session?

- 12
- 31
- 51
- 81

> [!TIP]
> **My Answer:**
> For this question, we have to use a **Session Window** to find the longest "busy streak" at any location.
>
> #### Comparison Table: Session vs Tumbling
> | Feature | Tumbling Window (Q4) | Session Window (Q5) |
> | :--- | :--- | :--- |
> | **Duration** | **Fixed** (5 mins). | **Dynamic** (Variable length). |
> | **Trigger** | Clock-aligned (08:05). | Event-aligned (Starts on first pickup). |
> | **Closure** | Fixed 5 min mark. | 5-minute gap of inactivity (silence). |
> | **Objective** | Peak Moment / Surge. | Longest continuous "streak". |
>
> The code for this job is essentially the same as in Question 4, but we **replaced the `TUMBLE` window function with a `SESSION` window** as follows:
> ```sql
> GROUP BY SESSION(event_timestamp, INTERVAL '5' MINUTE), PULocationID
> ```
>
> **Steps Taken:**
> 1.  **Initialize PostgreSQL Table:**
>     ```bash
>     docker exec -it homework-postgres-1 psql -U postgres -d postgres -c "
>     CREATE TABLE IF NOT EXISTS processed_session_counts (
>         window_start TIMESTAMP,
>         window_end TIMESTAMP,
>         PULocationID INTEGER,
>         num_trips BIGINT
>     );"
>     ```
> 2.  **Submit Session Job:**
>     ```bash
>     docker exec -it homework-jobmanager-1 flink run -py /opt/src/job/question_5.py
>     ```
> 3.  **Query Results:**
>     ```sql
>     docker exec -it homework-postgres-1 psql -U postgres -d postgres -c "
>     SELECT PULocationID, num_trips, window_start, window_end
>     FROM processed_session_counts
>     ORDER BY num_trips DESC
>     LIMIT 3;"
>     ```
> **Output:**
> ```text
>  pulocationid | num_trips |    window_start     |     window_end      
> --------------+-----------+---------------------+---------------------
>            74 |        81 | 2025-10-08 06:46:14 | 2025-10-08 08:27:40
>            74 |        72 | 2025-10-01 06:52:23 | 2025-10-01 08:23:33
>            74 |        71 | 2025-10-22 06:58:31 | 2025-10-22 08:25:04
> (3 rows)
> ```
> The answer is **81**.
> 

## Question 6. Tumbling window - largest tip

Create a Flink job that uses a 1-hour tumbling window to compute the
total `tip_amount` per hour (across all locations).

Which hour had the highest total tip amount?

- 2025-10-01 18:00:00
- 2025-10-16 18:00:00
- 2025-10-22 08:00:00
- 2025-10-30 16:00:00

> [!TIP]
> **My Answer:**
> We finished with the final question using a 1-hour tumbling window.
>
> **Step 1: Create the Sink Table**
> ```bash
> docker exec -it homework-postgres-1 psql -U postgres -d postgres -c "
> CREATE TABLE IF NOT EXISTS processed_hourly_tips (
>     window_start TIMESTAMP,
>     total_tip DOUBLE PRECISION
> );"
> ```
> 
> **Step 2: Submit the Flink Job**
> ```bash
> docker exec -it homework-jobmanager-1 flink run -py /opt/src/job/question_6.py
> ```
> 
> **Step 3: Query for busiest hour**
> ```sql
> docker exec -it homework-postgres-1 psql -U postgres -d postgres -c "
> SELECT window_start, total_tip
> FROM processed_hourly_tips
> ORDER BY total_tip DESC
> LIMIT 1;"
> ```
> **Output:**
> ```text
>     window_start     |     total_tip     
> ---------------------+-------------------
>  2025-10-16 18:00:00 | 510.8599999999999
> (1 row)
> ```
> The answer is **2025-10-16 18:00:00**. 
