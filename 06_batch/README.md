# Module 06: Batch Processing

This file contains my notes on Module 06 of the Data Engineering course.

The following materials from the official course have been downloaded into the `06_batch/` directory:
*   [code/](file:///workspaces/data-engineering-zoomcamp/06_batch/code): Contains lecture notebooks, scripts, and homework for the module.
*   [setup/](file:///workspaces/data-engineering-zoomcamp/06_batch/setup): Contains guides for installing Spark on different operating systems.

## 1. Introduction 

### 1.1. Introduction to Batch Processing

There are two primary ways of processing data:
1.  **Batch Processing**: Data is processed in discrete blocks or "batches" at specific intervals (one single job).
2.  **Streaming Processing**: Data is processed continuously as it arrives.

### Characteristics
*   **Frequency**: Jobs can be scheduled weekly, daily, hourly, or even every few minutes. The most common intervals are **daily** or **hourly**.
*   **Advantages**: Convenient, easy to manage, reliable, and allows for complex transformations.
*   **Disadvantages**: Significant **delay** (latency) between data generation and availability.

Despite this, the advantages of batch processing often outweigh the disadvantages. In most companies, the vast majority of data processing remains batch-oriented due to its robustness and lower operational complexity compared to streaming.

### Technologies Used
*   **Python Scripts**: Primarily used for data ingestion and light orchestration.
*   **SQL**: Used for data transformations (Dbt, BigQuery).
*   **Spark**: Used for **large-scale data processing** and heavy-duty transformations that benefit from parallel computation.
*   **Orchestration**: A typical workflow involves tools like **Airflow** to manage the pipeline dependencies and scheduling.


### 1.2. Introduction to Apache Spark

### 1.2.1. What is Apache Spark?
Apache Spark is a powerful, open-source **distributed computing engine** designed for large-scale data processing. It operates across a **cluster** of machines to process data stored in architectures ranging from **Data Lakes** to **Data Warehouses**.

**Key Features:**
*   **Multi-language Support**: While written in **Scala**, it provides high-level APIs for **Python (PySpark)**, **Java**, and **R**.
*   **Unified Engine**: PySpark is versatile, supporting both **Batch Processing** and **Stream Processing**.
*   **Performance**: Uses in-memory processing to stay significantly faster than traditional MapReduce jobs.

#### 1.2.2. When and Why to Use Spark?
Spark is typically used when data resides in a **Data Lake** (e.g., S3 or GCS) in formats like **Parquet**. Spark extracts the data, processes it, and often writes the results back to the Data Lake.

**Decision Framework: SQL vs. Spark**
*   **Rule of Thumb**: If you can express a job in **SQL**, use SQL (BigQuery, Snowflake, Presto, Athena). It is generally easier to maintain and optimize.
*   **Use Spark When**:
    *   The logic is too complex for standard SQL.
    *   You need specialized data processing (e.g., graph processing or advanced text manipulation).
    *   **Machine Learning**: Spark is the industry standard for training and applying models at scale.

#### 1.2.3. Typical Workflows
A standard enterprise data pipeline often looks like this:
1.  **Ingestion**: Raw data is landed in a **Data Lake**.
2.  **SQL Layer**: Initial transformations (joins, filtering) are performed using SQL.
3.  **Spark Layer**: Complex business logic or ML-specific preparations are handled via Spark.
4.  **Machine Learning**: Models are trained on the processed data.
5.  **Inference**: Spark is used to apply a trained model to massive datasets (Inference), sending results back to the Data Lake and finally into a **Data Warehouse** for reporting.


## 2. Installation 
We are using **GitHub Codespaces** running **Ubuntu 24.04.3 LTS (Noble Numbat)**. Spark can be installed directly using Python via the `pyspark` package, which bundles the Spark binaries.

### 2.1. Prerequisites
- **Java**: Java 25 is pre-installed at `/usr/local/sdkman/candidates/java/current`.
- **uv**: The modern Python package manager `uv` is recommended for managing dependencies.

### 2.2. Installation Steps
1.  **Initialize the Environment**:
    Navigate to the `06_batch/` folder and initialize a new `uv` project:
    ```bash
    uv init
    ```
2.  **Add PySpark**:
    Install the PySpark library (this includes the necessary Spark binaries):
    ```bash
    uv add pyspark
    ```

### 2.3. Verification
Create a simple `test_spark.py` script to confirm Spark is working:
```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

print(f"Spark version: {spark.version}")
df = spark.range(10)
df.show()
spark.stop()
```

Run the validation:
```bash
uv run python test_spark.py
```

### 2.4. Test Results & Explanation
The script executed successfully with the following output:
```text
Spark version: 4.1.1
+---+
| id|
+---+
|  0|
|  1|
|  2|
|  3|
|  4|
|  5|
|  6|
|  7|
|  8|
|  9|
+---+
```

**Note on Java Compatibility**: 
The default Java version in this Codespace is **Java 25**, which is not yet fully supported by current Spark versions (the Hadoop libraries specifically). This leads to an `UnsupportedOperationException: getSubject is not supported` when attempting to read or write files.

To fix this within your Jupyter Notebooks, you must set the environment variables **at the very top** of your notebook manually and restart the kernel:

```python
import os
import sys

# 1. Point JAVA_HOME to Version 21 (pre-installed in this Codespace)
os.environ["JAVA_HOME"] = "/usr/local/sdkman/candidates/java/21.0.9-ms"

# 2. Add Java 21 to the system PATH so Spark finds it first
os.environ["PATH"] = os.environ["JAVA_HOME"] + "/bin:" + os.environ["PATH"]

# 3. VERIFY - Should show Java 21 (OpenJDK 21.x.x)
!java -version
```

**CRITICAL**: After running this cell, you **must restart the kernel** (using the circular arrow button in VS Code) and then run your cells again starting from the top.


### 2.5. Jupyter Notebook Setup
To use PySpark within Jupyter Notebooks in this Codespace, follow these steps to ensure the correct virtual environment is used:

1.  **Install `ipykernel`**:
    Add `ipykernel` to your dependencies:
    ```bash
    uv add ipykernel
    ```

2.  **Register the Kernel**:
    Register the virtual environment as a Jupyter kernel so it's discoverable:
    ```bash
    uv run python -m ipykernel install --user --name spark_module_06 --display-name "PySpark (Module 06)"
    ```

3.  **Selecting the Kernel in VS Code**:
    *   Open your notebook (e.g., `code/03_test.ipynb`).
    *   In the top-right corner, click **"Select Kernel"**.
    *   Choose **"Python Environments..."** and select the one pointing to `.venv` (e.g., `Python 3.13.11 (.venv)`).
    *   Alternatively, you can select the registered **"PySpark (Module 06)"** kernel under the **"Jupyter Kernel..."** category.

4.  **Validation**:
    Verify the installation by running the following cell in your notebook:
    ```python
    import pyspark
    print(pyspark.__version__)
    ```
    The output should be `4.1.1`.
 
## 2.6. Initial Test: 03_test.ipynb
The `03_test.ipynb` notebook serves as a "Hello World" for PySpark in this module. It verifies the environment by performing the following operations:

1.  **Environment Check**: Confirms that Python can locate the `pyspark` libraries.
2.  **Spark Session Initialization**: Starts a local Spark cluster using `.master("local[*]")`, which utilizes all available CPU cores for parallel processing.
3.  **Data Ingestion**: Downloads the NYC Taxi Zone Lookup dataset (CSV) and loads it into a Spark DataFrame.
4.  **DataFrame Operations**: Uses `df.show()` to display the first 20 rows of the dataset, confirming the distributed computing engine is functioning.
5.  **Format Conversion**: Writes the DataFrame to **Parquet** format. This is a critical data engineering step, as Parquet is a columnar storage format optimized for Spark, providing better compression and performance than CSV.

Successfully running this notebook confirms that the Spark cluster is healthy and the environment is ready for large-scale data processing.

## 3. Spark SQL and DataFrames 

### 3.1. First look at Spark/PySpark
The notebook containing the first look at Spark is [04_pyspark.ipynb](code/04_pyspark.ipynb).
I had to force Spark to use the JAVA version 21 (higher versions give compatibility issues with the Spark version I was currently using).
Upon initializing the `SparkSession`, a **Spark Web UI** is started (typically accessible locally on port 4040), which provides a detailed dashboard to monitor the status of Spark jobs, visualize the physical execution plan (DAG), and inspect environment details.

**Tracked Pipeline Steps:**
1. **Initialize SparkSession**: Created a local Spark session which spun up the Spark UI.
2. **Initial Data Ingestion**: Downloaded the FHVHV January 2021 dataset and read it into Spark. Spark defaults all columns to strings.
3. **Schema Inference (using Pandas)**: To avoid forcing Spark to read the entire dataset just to infer data types (which is slow), we extracted a small 1000-line sample (`head.csv`). This sample was read with Pandas to quickly infer proper types.
4. **Schema Definition**: We translated the inferred Pandas schema into a PySpark `StructType` schema. Since Spark is built on Scala, we use PySpark's `types` module (e.g., `StructType`, `IntegerType`) to define the schema natively in Python. To optimize memory, we also manually downcasted `LongType` (which uses 8 bytes) to `IntegerType` (which uses 4 bytes).
5. **Repartitioning**: We repartitioned the DataFrame into **24 partitions** using `df.repartition(24)`. This is a key step for parallelism — Spark processes each partition independently and in parallel across executor cores. A common rule of thumb is to target **2–4 partitions per CPU core**; with ~8 cores available, 24 partitions keeps all cores busy across multiple waves without the overhead of too many tiny partitions. Each partition also writes out as its own individual **Parquet file** when `df.write.parquet(...)` is called.

#### Key Concept: Lazy Evaluation
Spark uses **lazy evaluation**, meaning it does not execute code immediately when you call most operations. Instead, it builds up a logical execution plan (a DAG) in memory and waits.

There are two types of operations:
- **Transformations** (e.g., `spark.read.csv(...)`, `df.repartition(24)`, `df.withColumn(...)`, `df.filter(...)`) — these are **lazy**. Spark records *what* to do, but does nothing yet. No jobs will appear in the Spark Web UI.
- **Actions** (e.g., `df.show()`, `df.count()`, `df.write.parquet(...)`, `df.collect()`) — these **trigger execution**. Spark compiles the full DAG and sends work to the executors. Only at this point will jobs appear in the Spark Web UI.

This is why you may run several cells without seeing any activity in the UI — it only lights up when an action is called.

#### How does Spark process the data?
Spark processes data from a cloud data lake, such as Google Cloud Storage (GCS), by utilizing a decoupled architecture where compute and storage scale independently.
When a Spark job is initiated, the Driver node coordinates with the GCS Connector to partition the remote data into distributed tasks. Individual Executor nodes then pull these data partitions over the network into their local RAM to perform parallel transformations and actions. Once processing is complete, the results are streamed back to the data lake as partitioned files (such as Parquet or Avro) or loaded into a managed warehouse like BigQuery.


### 3.2. Spark DataFrames

This section continues in the same notebook [04_pyspark.ipynb](code/04_pyspark.ipynb), picking up after the data has been read in with the correct schema and repartitioned. A Spark **DataFrame** is a distributed, tabular data structure similar to a Pandas DataFrame, but designed to run across a cluster.

Key DataFrame operations covered in this section:
- **`df.printSchema()`** — prints the column names and their types in a readable tree format.
- **`df.select(...)`** — selects a subset of columns (equivalent to `SELECT` in SQL).
- **`df.filter(...)`** — filters rows based on a condition (equivalent to `WHERE` in SQL).
- **`df.withColumn(...)`** — adds or replaces a column, using built-in functions from `pyspark.sql.functions`.
- **`df.groupBy(...)`** — groups rows by one or more columns and allows aggregate functions (e.g., `.count()`, `.sum()`, `.avg()`) to be applied — equivalent to `GROUP BY` in SQL.
- **`df.join(...)`** — joins two DataFrames together on a common key — equivalent to `JOIN` in SQL, supporting inner, left, right, and outer join types.
- **User Defined Functions (UDFs)** — custom Python functions registered with Spark using `F.udf(...)`, allowing arbitrary logic to be applied to each row in a distributed way.

#### What can we do with a DataFrame?

**1. Select specific columns** using `df.select(...)`:
```python
df.select('pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID')
```
This is a **transformation** — it returns a new DataFrame with only the chosen columns, without running anything yet.

**2. Filter rows** using `df.filter(...)`:
```python
df.select('pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID') \
  .filter(df.hvfhs_license_num == 'HV0003')
```
This is also a **transformation**. Only when chained with an action (like `.show()` or `.collect()`) will Spark execute both steps together in one optimised pass — this is one of the key benefits of lazy evaluation.

> **Note**: The distinction between transformations and actions (lazy evaluation) is covered in detail in the [Key Concept: Lazy Evaluation](#key-concept-lazy-evaluation) section above.

#### Built-in SQL Functions (`pyspark.sql.functions`)
PySpark also has a set of **built-in functions that mirror standard SQL functions**, allowing us to perform common transformations (date manipulation, string operations, aggregations, etc.) directly in Python without writing raw SQL. They are available through the `pyspark.sql.functions` module, typically imported as:
```python
from pyspark.sql import functions as F
```
These mirror standard SQL functions and are highly optimised to run natively on Spark's JVM engine (much faster than Python UDFs). Common examples include:
- `F.to_date(col)` — converts a timestamp column to a date.
- `F.year(col)`, `F.month(col)` — extracts date parts.
- `F.col(name)` — references a column by name.
- `F.lit(value)` — creates a column with a constant/literal value.
- `F.count(...)`, `F.sum(...)`, `F.avg(...)` — aggregate functions.

Whenever possible, prefer built-in functions over Python UDFs for better performance.
For example: Adding new columns with `df.withColumn(...)` and `F.to_date(...)`:

A very common real-world need is to extract just the **date** from a full timestamp column. For example, `pickup_datetime` contains values like `2021-01-01 00:33:44`, but often you only need `2021-01-01` for daily aggregations.

We use `withColumn` to add a new column, and `F.to_date(...)` to perform the conversion:

```python
from pyspark.sql import functions as F

df \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .withColumn('dropoff_date', F.to_date(df.dropoff_datetime)) \
    .select('pickup_date', 'dropoff_date', 'PULocationID', 'DOLocationID') \
    .show()
```

What's happening step by step:
- **`F.to_date(df.pickup_datetime)`** — takes the full timestamp column and strips the time portion, returning only the date (e.g., `2021-01-01`).
- **`.withColumn('pickup_date', ...)`** — adds a new column called `pickup_date` to the DataFrame with the result. The original `pickup_datetime` column is **not removed** — it still exists alongside the new one.
- The same is done for `dropoff_datetime`.
- Finally, `.select(...)` keeps only the columns we care about, and `.show()` triggers the execution.

> `withColumn` is a **transformation** — it does not modify the original DataFrame in place. Instead, it returns a **new** DataFrame with the extra column added. This is because DataFrames in Spark (and pandas) are **immutable**.

#### User Defined Functions (UDFs)

Some transformations are too complex or custom to express in standard SQL. For those cases, PySpark lets you wrap any Python function into a **UDF (User Defined Function)** and apply it to a DataFrame column in a distributed way.

In the notebook, the `crazy_stuff` function is a simple example: it takes a dispatching base number (e.g. `B02884`), strips the letter, and encodes it into a short string based on divisibility rules.

```python
from pyspark.sql import functions as F
from pyspark.sql import types

def crazy_stuff(base_num):
    num = int(base_num[1:])
    if num % 7 == 0:
        return f's/{num:03x}'
    elif num % 3 == 0:
        return f'a/{num:03x}'
    else:
        return f'e/{num:03x}'

# Register it as a UDF so Spark can use it across the cluster
crazy_stuff_udf = F.udf(crazy_stuff, returnType=types.StringType())

# Use it in a transformation chain
df \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .withColumn('dropoff_date', F.to_date(df.dropoff_datetime)) \
    .withColumn('base_id', crazy_stuff_udf(df.dispatching_base_num)) \
    .select('base_id', 'pickup_date', 'dropoff_date', 'PULocationID', 'DOLocationID') \
    .show()
```

> **Note**: UDFs are powerful but slower than built-in functions, because Spark has to serialize data between the JVM and Python for every row. Use built-in `pyspark.sql.functions` whenever possible, and reserve UDFs for logic that truly can't be expressed any other way. Machine learning logic is usually one of these cases. 


### 3.3. Preparing Yellow and Green Taxi Data

This section was optional, so I followed the workaround to get the data directly (althougt it required some adaptations to my set up in Codespaces). Those were handled by Antigravity:

We implemented this step to prepare the full datasets for both Yellow and Green taxis for 2020 and 2021. This ensures consistency for the following [SQL with Spark](#34-sql-with-spark) section.

**Steps Performed:**
1. **Data Download**: Used the `download_data.sh` script to pull CSV data from the GitHub mirror.
   - **Green Taxi**: 2020 (all months) and 2021 (months 1-7).
   - **Yellow Taxi**: 2020 (all months) and 2021 (months 1-7).
   *Note: Months 08-12 for 2021 were skipped as the dataset ends in July 2021.*
2. **Schema Ingestion & Parquet Conversion**: Executed the `05_taxi_schema.ipynb` notebook.
   - Defined structured schemas for both taxi types to ensure data quality (fixing type mismatches like `VendorID` being read as strings).
   - Converted the raw `.csv.gz` files into partitioned **Parquet** files located in `data/pq/green/` and `data/pq/yellow/`.
   - Each month was repartitioned into **4 partitions** to optimize for local parallel processing.
3. **Environment Fixes**: (`fix_notebook.py`)
   - Manually forced **Java 21** within the notebook to avoid compatibility issues with the pre-installed Java 25.
   - Adjusted the processing loops to stop at month 07 for the 2021 datasets to prevent "Path does not exist" errors.

By converting the data to Parquet at this stage, we significantly improve the performance and reduce the memory footprint for all subsequent analysis and SQL queries.

### 3.4. SQL with Spark

This section, covered in [06_spark_sql.ipynb](code/06_spark_sql.ipynb), demonstrates how to use Spark's SQL interface to query DataFrames. This is particularly useful for teams that are more comfortable with SQL than Python, or for complex analytical queries that are more readable in SQL.

**Key Steps:**

1.  **Loading and Aligning Data**:

We loaded both Green and Yellow taxi Parquet data. 

Each dataset has its own specific columns (e.g., Green has `ehail_fee`) and naming conventions (e.g., `lpep_pickup_datetime` vs `tpep_pickup_datetime`). To integrate them into a single analytical table:

- **Issue**: Spark's `.unionAll()` requires both DataFrames to have the exact same columns in the same order.
- **Solution**: 
    - Renamed pickup/dropoff datetime columns to a shared `pickup_datetime` format.
    - Programmatically identified and selected only the **common columns** present in both schemas.
    - Added a `service_type` column (using `F.lit()`) to distinguish between 'green' and 'yellow' source data.

This integration process is detailed in the first cells of [06_spark_sql.ipynb](code/06_spark_sql.ipynb).

#### 2. Registering a Temporary View

To query a DataFrame with SQL, we must first register it as a temporary table or view. This creates a reference that the Spark SQL engine can understand:
```python
df_trips_data.registerTempTable('trips_data')
```
*Note: In newer Spark versions, `createOrReplaceTempView()` is preferred.*

#### 3. Executing SQL Queries

We can now use `spark.sql()` to perform the same operations we did with the DataFrame API. For example, a simple count:

| DataFrame API | Spark SQL |
| :--- | :--- |
| `df.groupBy('service_type').count().show()` | `SELECT service_type, count(1) FROM trips_data GROUP BY 1` |

Both produce the exact same result because they share the same internal optimizer.

#### 4. Complex Analytic Query (Monthly Revenue)

The final part of the notebook executes a large analytic query to calculate a **Monthly Revenue Report** per Pickup Location:
- Uses `date_trunc('month', ...)` to group data by month.
- Aggregates multiple fare components (`fare_amount`, `extra`, `tip_amount`, etc.).
- Calculates averages for passenger counts and trip distances.
- Groups by Location, Month, and Service Type.

#### 5. Output and Coalesce 📤

After the complex SQL transformation, we save the result back to the data lake:
```python
df_result.coalesce(1).write.parquet('data/report/revenue/', mode='overwrite')
```
**Why `coalesce(1)`?** 
Since the resulting "report" dataset is relatively small compared to the raw data, we use `coalesce(1)` to merge all small partitions into a **single Parquet file**. This makes it much easier to share or download the final report.

#### The Catalyst Optimizer 🧠

A common question is: **Is SQL slower than the DataFrame API?**
**Answer: No.**

Both the DataFrame API and the SQL API go through the exact same **Catalyst Optimizer**. 
- Whether you write `df.groupBy(...).count()` or `SELECT count(*) FROM ... GROUP BY ...`, Spark translates both into the same internal **Physical Plan**.
- This means you can choose the interface that makes your code more readable without worrying about performance trade-offs.

#### Output 📤
Finally, we saved the results of our complex SQL aggregation back to the Data Lake as a single Parquet file (using `.coalesce(1)`) into `data/report/revenue/`.


## 4. Spark internals

### 4.1. Anatomy of a Spark Cluster

Understanding how Spark manages resources is key to debugging and optimization. A Spark cluster consists of several components working together:

- **Driver**: This is the heart of the Spark application. It runs the `main()` function and creates the `SparkSession`. It is responsible for:
    - Converting the user code into tasks.
    - Scheduling tasks on the executors.
    - Communicating with the Cluster Manager.
- **Executor**: These are worker processes that live on the cluster nodes. They actually execute the tasks assigned by the Driver and store the data in memory/disk.
- **Cluster Manager**: A service like **YARN** (GCP Dataproc), **Kubernetes**, or Spark's Standalone manager that allocates resources across the cluster.

#### Data Locality and External Storage 💾
Unlike traditional Hadoop setups where data lives on the same nodes as the processing (HDFS), modern cloud Spark architectures often use **External Storage** (GCP GCS or AWS S3):
1. The **Driver** pulls the metadata from the file.
2. The **Executors** pull the actual blocks of data from the Data Lake.
3. If an Executor dies, the Driver just spawns a new one to pull that data again—this makes Spark highly resilient.

### 4.2. GroupBy in Spark
    
Spark performs grouping and aggregation in two distinct stages to minimize data transfer over the network (shuffling).

1.  **Stage 1: Map-Side Aggregation**: 
    Each executor processes its assigned partitions independently. It filters the data and performs a **partial aggregation** (e.g., calculates sub-totals or partial counts for each key within that specific partition). This is efficient because it happens in-memory without network communication.
2.  **The Shuffle**: 
    Spark redistributes the intermediate sub-totals across the cluster so that all data belonging to the same key ends up on the same executor. This is the most "expensive" part as it involves moving data over the network.
3.  **Stage 2: Reduce (Final Aggregation)**: 
    The executors receive all intermediate sub-totals for their assigned keys and combine them to produce the final, global result.

> [!TIP]
> This two-stage process is why Spark is efficient; by performing a "local summary" first, it reduces the number of records that must travel through the network during the Shuffle phase.

### 4.3. Joins in Spark

Joining two large tables is the ultimate test for a Spark cluster. Spark uses two main strategies depending on the size of the data:

#### 1. Sort Merge Join (The Default) 🔄
Used when joining two large tables.
1. **Shuffle**: Both tables are shuffled so all records with the same joining key end up on the same executor.
2. **Sort**: Each partition is sorted by the joining key.
3. **Merge**: Spark iterates through both sorted lists once and merges matching rows.

#### 2. Broadcast Join (The Optimizer's Favorite) 📡
Used when one table is small (e.g., a "Zone" lookup table) and the other is large (millions of taxi trips).
1. The **Driver** sends the *entire* small table to **every executor**.
2. Each executor stores the small table in its local memory.
3. The large table is processed locally without **any shuffling**.

*Note: In PySpark, you can hint at this by using `from pyspark.sql.functions import broadcast` and then `big_df.join(broadcast(small_df), ...)`.*

## 5. Resilient Distributed Datasets (RDDs)

**Resilient Distributed Datasets (RDDs)** are the fundamental data structure of Spark. While we have been using DataFrames, it's important to understand the engine that powers them.

- **Resilient**: Ability to re-compute missing data automatically if a node fails.
- **Distributed**: Data is partitioned across the cluster.
- **Relation to DataFrames**: DataFrames are actually built *on top* of RDDs. Think of an RDD as a raw list of objects without a schema, while a DataFrame is that same list but with a structured "table" view (columns and types) that allows for automatic optimization.

> [!IMPORTANT]
> **Skipping RDD Exercises**: Since modern Spark development (and this course's homework) focuses almost entirely on the **DataFrame API** and **Spark SQL** for better performance and readability, we are skipping the low-level RDD implementation exercises.

### 5.1. Operations on Spark RDDs (Skipped)
### 5.2. Spark RDD mapPartition (Skipped)

## 6. Running Spark in the Cloud

### 6.1. Connecting to Google Cloud Storage
### 6.2. Creating a Local Spark Cluster
### 6.3. Setting up a Dataproc Cluster
### 6.4. Connecting Spark with BigQuery