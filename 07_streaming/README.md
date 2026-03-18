# Module 07: Streaming (Real-Time Data Engineering)

These are my notes on the final module of the Data Engineering Zoomcamp. Here, we transition from batch processing to **Streaming**. This section covers the complexities of real-time data engineering, moving from basic Python-based Kafka consumers to enterprise-grade Apache Flink pipelines.

## 1. Introduction 

### 1.1. What is Streaming?
Streaming is a data processing paradigm where records are processed individually or in small micro-batches as they arrive, rather than waiting for a large set of data to be collected (Batch).

- **Unbounded Data**: Unlike batch (bounded) datasets, streams have no defined end; they are continuous.
- **Low Latency**: Processing happens in real-time or near real-time (milliseconds to seconds).
- **Event-Driven**: The system reacts to individual events as they occur (e.g., a taxi trip finishing, a credit card swipe).

### 1.2. Introduction to Apache Kafka
Apache Kafka is an open-source **distributed event store** and stream-processing platform. It acts as a central hub that allows different parts of a system to communicate asynchronously via events.

#### Core Concepts:
- **Topic**: A logical category where events are stored (similar to a table in a DB).
- **Partition**: Topics are split into partitions to allow multiple consumers to read data in parallel.
- **Broker**: A node in the Kafka cluster. Multiple brokers work together to ensure data is redundant and available.
- **Producer**: An application that pushes ("publishes") events into a topic.
- **Consumer**: An application that reads ("subscribes") events from a topic.
- **Consumer Group**: A group of consumers that work together to consume data from a topic, ensuring each message is processed only once within the group.

#### Why use a Message Broker?
In a traditional setup, every service has to talk to every other service (Point-to-Point). With a broker like Kafka:
1. **Decoupling**: The producer doesn't need to know who the consumer is or if they are even online.
2. **Buffering**: If a consumer is slow or goes down, Kafka stores the messages until the consumer is ready again.
3. **Immutability**: Once an event is written to Kafka, it cannot be changed, providing a reliable audit log.

### 1.3. Environment Setup
Maintaining consistency with previous modules, we are utilizing **GitHub Codespaces** as our primary development environment. 
- **Python Management**: We use `uv` for environment isolation and dependency management.
- **Docker**: Essential for running our lightweight message broker (**RedPanda**) in a containerized way within the Codespace.

> [!TIP]
> **Project Initialization**
>
> We started by initializing a `uv` project specifically with **Python 3.12**:
> ```bash
> uv init --python 3.12
> ```
> **Technical Note**: We use version **3.12** because, at the time of writing, **Apache Flink** does not yet support Python 3.13.
>
> We then added the essential libraries for our streaming tasks:
> ```bash
> uv add kafka-python-ng pandas pyarrow
> ```

### 1.4. Technical Architecture
In the GitHub Codespaces ecosystem, **GitHub Codespaces** functions as the host Virtual Machine (VM), providing the underlying Linux operating system, CPU, RAM, and storage. **uv** operates as a Python-specific environment orchestrator that manages the installation of library dependencies (like `pandas` or `kafka-python-ng`) inside an isolated virtual environment; it ensures your Python scripts have the correct runtime and packages to execute application-level logic. **Docker** (managed via Docker Compose) is used to run independent infrastructure services such as **RedPanda**; these are standalone binary applications that require their own system-level configurations and resources, and therefore cannot be installed as Python libraries. Within the Codespace, the Python process running in your `uv` environment acts as a **client** that communicates over the local network (typically via `localhost` ports) with the **server** containers managed by Docker, allowing your code to produce and consume data from the streaming infrastructure.

### 1.5. Tools and Libraries
Within our `uv` environment, we utilize several key libraries for this module:
- **`kafka-python-ng`**: The modern Python client used to connect with the Kafka protocol (and by extension, RedPanda).
- **`pandas`**: A high-performance data manipulation library used for processing and transforming the taxi datasets before streaming.
- **`pyarrow`**: Provides the necessary backend to read Parquet files efficiently.
- **`psycopg2-binary`**: The PostgreSQL adapter for Python. It acts as the "driver" that allows our Python scripts to connect and write data to the Postgres database.

### 1.6. Infrastructure (Docker)
We use a `docker-compose.yml` file to manage our local infrastructure. For this module, the primary service is **RedPanda**.

- **RedPanda**: A lightweight, Kafka-compatible streaming platform that acts as our message broker.
- **PostgreSQL**: A relational database used as a "Sink" to persist our processed streaming data.
- **Apache Flink**: A distributed processing engine for stateful computations over data streams.

### 1.7. Practical Setup
Commands executed to start the infrastructure and prepare the environment:
```bash
# 1. Start Initial Infrastructure (Redpanda & Postgres)
docker compose up redpanda postgres -d

# 2. Add the PostgreSQL connector to our local environment
uv add psycopg2-binary

# 3. Build & Start the Flink Cluster
# First, ensure the 'src' folder exists for the Volume Mount
mkdir -p src 

# Build the hybrid Java/Python image
docker compose build

# Bring up the JobManager and TaskManager
docker compose up -d
```

> [!TIP]
> **Patience is Key**: After running `docker compose up`, Redpanda may take 15-20 seconds to fully initialize its Kafka API. If you get a `ValueError: Invalid file object: None` in your notebook immediately after starting, just wait a few moments and try running the cell again.

### 1.8. Verification
Once the cluster is up, you can verify the status of the services:
```bash
docker ps
```

You should see 4 containers running: `jobmanager`, `taskmanager`, `redpanda`, and `postgres`. You can also access the **Flink Web UI** at `http://localhost:8081` to see the available task slots.

To interact with the database, we use **pgcli**, a command-line interface for Postgres with auto-completion and syntax highlighting. We run it using **`uvx`**, which executes the tool in a temporary, isolated environment without needing to install it globally:
```bash
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

### 1.9. Producers and Consumers
To interact with our streaming cluster, we use two main components:
- **Producer**: An application (in our case, a Python script) that takes data—like our Green Taxi records—and sends it as a stream of events into a specific RedPanda **Topic**. Something that writes to this kfka stream.
- **Consumer**: An application that subscribes to a topic to read and process the incoming stream of events. Consumers can be used for real-time dashboards, database ingestion, or further data transformations. Something that is reading from this Kafka stream. 

We have created a `notebooks/` directory to host our experimental producer and consumer logic using Jupyter.

To experiment with our streaming logic in an interactive environment, we add Jupyter as a development dependency:

```bash
uv add --dev jupyter
```
---
Then we need to **register** the kernel so it's available in the Jupyter interface:

uv run python -m ipykernel install --user --name 07-streaming --display-name "Python 3.12 (07-streaming)"

### 1.10. Data Modeling & Serialization

To ensure consistent data structures across our producers and consumers, we define our events using Python **Dataclasses**. An event represents a single occurrence of an action—in our case, a recorded taxi ride.

#### The `Ride` Model
We use a central [models.py](file:///workspaces/data-engineering-zoomcamp/07_streaming/notebooks/models.py) file to define the schema of our event. The `Ride` class captures the essential details of each trip:

- **`PULocationID` & `DOLocationID`**: Pick-up and drop-off locations (integers).
- **`trip_distance`**: The length of the trip (float).
- **`total_amount`**: The cost of the ride (float).
- **`tpep_pickup_datetime`**: The timestamp of the ride, stored as **epoch milliseconds** (integer). This format is crucial for compatibility with stream processing frameworks like Apache Flink.

#### Serialization (Object to Bytes)
Kafka is data-agnostic; it doesn't understand Python objects. It only stores and transmits **bytes**. To bridge this gap, we use a multi-step transformation:

1.  **Ride Object**: We work with clean Python objects for readability.
2.  **Dictionary (The Middle-man)**: Because the `json` library doesn't understand custom Python classes, we first convert the object into a standard dictionary.
3.  **JSON String**: We encode that dictionary into a universal JSON format.
4.  **Bytes**: Finally, we convert the string into UTF-8 bytes to be sent to Redpanda.

The `ride_serializer` function in `models.py` handles this "Object → Dict → JSON → Bytes" journey, ensuring our data is in a format that any system can understand while keeping our Python code clean.

---



## 🏗️ Chapter 1: Introduction to Streaming Architecture

Real-time data engineering involves handling high-velocity data and stateful aggregations.

### 1.1 Kafka vs. Red Panda
Apache Kafka is historically the industry standard, but it can be **heavy and complex** to run locally for testing (due to the JVM and ZooKeeper/KRaft overhead). 

For this reason, we are using **RedPanda** as a lightweight replacement:
- **Fast & Simple**: Written in C++, it has a much smaller footprint and starts up quickly.
- **Kafka-Compatible**: It use the same Kafka wire protocols, meaning our existing Kafka-based Python libraries and tools will work without any modification.
- **Modern**: It handles high-performance streaming without the JVM complexity, making it ideal for local development and testing.

### 1.2 The Producer & Consumer Pattern
The fundamental communication pattern in streaming:
- **Producer**: Turning Python data (or any object) into streamable bytes and sending them to a cluster.
- **Consumer**: Subscribing to topics to read those bytes back and process them.

---

## ⚙️ Chapter 2: Stream Processing & Data Ingestion

### 2.1 Database Integration (Sinks)
The `consumer_db.ipynb` serves as our **Data Sink**. Its role is to bridge the gap between live streams and persistent storage.

**Key Responsibilities:**
- **Subscribe**: Listens specifically to the `rides` topic.
- **Deserialize**: Uses our custom `ride_deserializer` to automatically turn bytes into Python objects.
- **Persist**: Performs SQL `INSERT` operations to save each event into **PostgreSQL**.
- **Continuity**: The `auto_offset_reset='earliest'` setting ensures no data is missed, even if the consumer starts late.

#### Database Schema
Before running the consumer, we must create the destination table. This schema matches the attributes of our Python `Ride` model. We connect using `pgcli` and execute the following:

```bash
uvx pgcli -h localhost -p 5432 -U postgres -d postgres
```

```sql
CREATE TABLE processed_events (
    PULocationID INTEGER,
    DOLocationID INTEGER,
    trip_distance DOUBLE PRECISION,
    total_amount DOUBLE PRECISION,
    pickup_datetime TIMESTAMP
);
```
- **Note**: The `pickup_datetime` is converted from "epoch milliseconds" in Python to a proper SQL `TIMESTAMP` by the consumer script before insertion.
- **Why `psycopg2-binary`?**: We use the `-binary` version in development environments because it comes with pre-compiled C libraries, making the installation fast and reliable within our Codespace.

#### Verifying the Pipeline
To check if data is correctly moving from the stream into the database, run the following SQL command in `pgcli`:

```sql
SELECT COUNT(1) FROM processed_events;
```

*   **Result = 0**: The pipeline is successfully connected and the table is ready, but no data has been produced yet.
*   **Result > 0**: Success! Data is flowing from Redpanda → Consumer → PostgreSQL. This confirms the entire "Data Sink" journey is operational.


### 2.2 Apache Flink Fundamentals
While our Python Consumer is great for moving data, **Apache Flink** is a specialized stream processing engine designed for complex, real-time transformations. It allows us to perform "Stateful" computations—like calculating running totals or averages—directly on the stream without needing to query a database first.

#### Why Flink?
- **Low Latency**: Processes events the millisecond they arrive.
- **Fault Tolerance**: Uses "Checkpoints" to ensure data is never lost or double-counted, even if a node fails.
- **Event Time Processing**: Can handle data that arrives late or out of order by using "Watermarks."

#### Flink vs. Spark Streaming
Since we used Spark in previous modules, it's important to understand the difference. Flink is a **Native Streaming** engine, whereas Spark is primarily a **Batch** engine that simulates streaming.

| Feature | Apache Flink | Apache Spark |
| :--- | :--- | :--- |
| **Processing Model** | Continuous (Event-at-a-time) | Micro-batching |
| **Latency** | Very Low (Milliseconds) | Low (Seconds) |
| **State Handling** | Native, highly sophisticated | Managed through Structured Streaming |
| **Best For** | Real-time fraud detection, IoT | Large-scale ETL, Machine Learning |

#### Key Resilience: Checkpointing
Unlike batch pipelines that can simply be restarted, a streaming job runs 24/7. **Checkpointing** is Flink's mechanism for fault tolerance:
- **Snapshots**: Flink takes periodic "snapshots" of the entire job state (Kafka offsets, window contents, etc.).
- **Recovery**: If a node fails, Flink rolls back to the last successful checkpoint and resumes processing without losing data or creating duplicates.
- **Trade-off**: Frequent checkpoints (e.g., every 1 second) provide high resilience but add performance overhead.

### 2.3 The "Pass-Through" Job
A "Pass-Through" job is the simplest Flink pipeline: it reads data from a source (Kafka) and writes it directly to a sink (PostgreSQL) without transformation. 

**Why use Flink for this?**
Even for simple moves, Flink provides **declarative DDLs**. Instead of writing `psycopg2` `INSERT` loops, we define tables:

```sql
CREATE TABLE processed_events (
    PULocationID INTEGER,
    DOLocationID INTEGER,
    trip_distance DOUBLE,
    total_amount DOUBLE,
    pickup_datetime TIMESTAMP
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://postgres:5432/postgres',
    'table-name' = 'processed_events',
    'username' = 'postgres',
    'password' = 'postgres'
);
```
The engine handles the connection pooling, batching, and offset management automatically.

### 2.4 Infrastructure & Connectivity (The Flink Cluster)
To run Python code (PyFlink) inside a Flink cluster, we use a custom Docker architecture. This answers why we have a specialized `Dockerfile.flink`:

#### The Hybrid Environment
Apache Flink is a Java-based engine. To make it "speak" Python, our custom image performs several tasks:
1.  **Grafting Python**: We start with the official Flink Java image and use `uv` to install **Python 3.12** and the `apache-flink` library.
2.  **Connector Bridges (JARs)**: Flink uses Java Archives (`.jar` files) as bridges to external systems. The Dockerfile pre-downloads these:
    - **`flink-sql-connector-kafka`**: The driver for Redpanda/Kafka.
    - **`flink-connector-jdbc` & `postgresql.jar`**: The drivers used to write results into the database.
3.  **Lightweight Selection**: While your main Codespace has tools like Jupyter and Pandas, the Flink cluster only contains the bare essentials needed to execute the stream.

#### Cluster Components
- **Job Manager (The Brain)**: Coordinates job execution, accepts new tasks, and manages the checkpoints.
- **Task Manager (The Muscle)**: Performs the actual data movement and math. It has **Slots** (units of CPU/RAM) that allow it to process multiple parts of a job in parallel.

---

## 🕒 Chapter 3: Advanced Streaming Concepts

### 3.1 Handling Late Data (Watermarks)
In the real world, "Event Time" (when a taxi trip happened) and "Processing Time" (when the server sees it) are rarely the same. Data arrives late due to network lag or offline devices.

**The Watermark Solution:**
A Watermark is a "clock" that travels inside the data stream. It tells Flink: *"I am reasonably sure that no more events older than X will arrive."*
- **Patience**: We can set a watermark to be, for example, 5 seconds behind the latest event. 
- **Trigger**: When the watermark passes a window's end time, Flink closes that window and calculates the result.

### 3.2 Time Windows
Grouping continuous data into discrete blocks is essential for analytics. Flink supports three primary window types:

1.  **Tumbling Windows**: Fixed-size, non-overlapping (e.g., "Every 1 hour"). Best for standard periodic reporting.
2.  **Sliding Windows**: Fixed-size but overlapping (e.g., "The last 1 hour, updated every 15 minutes"). Best for finding peaks/surges.
3.  **Session Windows**: Dynamic size based on inactivity gaps. Best for user behavior analysis (e.g., "Group all clicks until the user is idle for 30 minutes").

---

## 🛠️ Chapter 5: Advanced Flink - Windowed Aggregation

While the "Pass-Through" job moves data, the **Aggregation Job** is where Flink really shines by performing real-time math on your streams.

### 5.1 The "Tumbling Window" Concept
Think of a Tumbling Window as a series of **non-overlapping timed buckets**. 
-   Each bucket (e.g., 1 hour) collects every ride that happens within that specific hour.
-   When the hour ends, the bucket "tumbles" away, Flink calculates the totals (sum of revenue, count of trips), and a single summary row is sent to the database.

### 5.2 The "Relay Race" Step-by-Step (Bear in Mind!)
When you run your pipeline, here is exactly what is happening for a single ride (e.g., **Ride #43**):

1.  **The Origin (Notebook)**: Your `producer.ipynb` reads Ride #43 from a Parquet file.
2.  **The Hand-off (Producer API)**: The notebook sends the data as bytes to **Redpanda** on port `9092`.
3.  **The Buffer (Redpanda)**: Redpanda stores the bytes in the `rides` topic. It doesn't process them; it just holds them safely.
4.  **The Engine (Flink)**: Flink’s `aggregation_job.py` is always "listening." It pulls Ride #43, checks its timestamp, and places it into the correct "1-Hour Bucket."
5.  **The Trigger (Watermark)**: Once Flink is sure that no more data for that hour is coming (based on the 5-second watermark), it closes the bucket.
6.  **The Destination (Postgres)**: Flink sends the final count and revenue for that entire hour to the `processed_events_aggregated` table.

### 5.3 Technical Implementation

#### The Aggregation Table (Postgres)
This table uses a **Composite Primary Key** to enable "Upserts." If a late ride arrives after the bucket has already been reported, Flink will send an "update" to correct the total in Postgres.

```sql
CREATE TABLE processed_events_aggregated (
    window_start TIMESTAMP,
    PULocationID INTEGER,
    num_trips BIGINT,
    total_revenue DOUBLE PRECISION,
    PRIMARY KEY (window_start, PULocationID)
);
```

#### The Aggregation Script (`aggregation_job.py`)
Key features of this job include:
-   **Watermarks**: Tells Flink to wait 5 seconds for "straggler" events before closing a window.
-   **TUMBLE Function**: Groups the data into fixed 1-hour intervals based on the pickup location.

```bash
# To run the aggregation job:
docker compose exec jobmanager ./bin/flink run \
    -py /opt/src/job/aggregation_job.py \
    --pyFiles /opt/src -d
```

### 5.4 Handling the "Real World" (Late Events)
In a real production environment, data rarely arrives in perfect order. To test this, we used **`producer_realtime.py`**, which intentionally simulates network delays.

#### 🌊 The Watermark "Patience" Window
Our script is configured with a **5-second Watermark**.
-   **On Time / Minor Delay (< 5s)**: Data is included in the window calculation immediately.
-   **Late Arrival (> 5s)**: The window has already been "closed" and reported to Postgres.

#### 🛠️ The Upsert Correction
When a "Late" event (like a 10-second delay) arrives, Flink doesn't ignore it. 
1.  Flink calculates the **new, corrected total** for that past hour.
2.  It sends an **UPDATE** command to Postgres using the **Composite Primary Key** (`window_start`, `PULocationID`).
3.  The database row is updated in-place, ensuring your dashboard is always 100% accurate eventually!

### 📊 Verifying the Results
Run this query in `pgcli` to see your live hourly taxi analytics:

```sql
SELECT 
    window_start, 
    count(*) as unique_locations, 
    sum(num_trips) as total_trips,
    round(sum(total_revenue)::numeric, 2) as hourly_revenue
FROM processed_events_aggregated
GROUP BY window_start
ORDER BY window_start;
```

---

## ❓ When to Use Streaming? (The Reality Check)

Streaming has a high operational cost (it runs 24/7 and needs monitoring). Before choosing Flink over Batch:
- **Is it for a machine?** If an automated system needs to react in seconds (fraud detection, surge pricing), use **Streaming**.
- **Is it for a human?** If the result is just for a dashboard that someone checks once a day, **Batch** is likely easier and cheaper.

---

## 🗒️ Next Actions
- [x] Setup Red Panda/Kafka cluster.
- [x] Implement Python Producer for Taxi Data.
- [x] Build and Start the Flink/PyFlink Cluster.
- [x] Run the Pass-Through Job.
- [x] Run the Windowed Aggregation Job.

---
*The journey ends with real-time mastery!* 🌊⚡
