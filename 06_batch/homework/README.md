# Module 6 Homework

In this homework we'll put what we learned about Spark in practice.

For this homework we will be using the Yellow 2025-11 data from the official website:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet
```


### Question 1: Install Spark and PySpark

**Run PySpark, create a local spark session, and execute `spark.version`. What's the output?**

> [!TIP]
> **My Answer:**
>
> **Installation Process:**
> I'm using Github Codespaces, and the installation was performed as follows:
> 1.  **PySpark**: Installed via `uv` (the package manager). The `pyspark` library includes the necessary Spark binaries for local execution.
>     ```bash
>     uv add pyspark
>     ```
> 2.  **Java**: Configured the environment to use **Java 21**, which is compatible with Spark 4.x.
> 3.  **Kernel**: Registered the virtual environment as a Jupyter kernel.
>
> **Spark Version Output:**
> ```python
> import pyspark
> from pyspark.sql import SparkSession
>
> spark = SparkSession.builder \
>     .master("local[*]") \
>     .appName('homework') \
>     .getOrCreate()
>
> print(spark.version)
> ```
> The output is `4.1.1` 


> [!TIP]
### Question 2: Yellow November 2025

**Read the November 2025 Yellow into a Spark Dataframe. Repartition the Dataframe to 4 partitions and save it to parquet. What is the average size of the Parquet Files that were created (in MB)?**

- 6MB
- 25MB
- 75MB
- 100MB

> [!TIP]
> **My Answer:**
> The answer is **25MB**.
>
> **Approach & Conclusion:**
> 1.  I read the original `yellow_tripdata_2025-11.parquet` file (~68MB).
> 2.  I applied `.repartition(4)`, which forces Spark to physically shuffle the data into 4 equal-sized partitions.
> 3.  The output produced 4 Parquet files in the destination folder.
> 4.  Checking with `ls -lh`, each file was approximately **25MB** (the exact size can vary due to Parquet compression and metadata, but 25MB is the closest match among the options).


### Question 3: Count records

**How many taxi trips were there on the 15th of November? Consider only trips that started on the 15th of November.**

- 62,610
- 102,340
- 162,604
- 225,768

> [!TIP]
> **My Answer:** 
> The answer is **102,340**. 
>
> **Approach:** 
> I used `F.to_date` to extract the date part and then filtered for '2025-11-15'.


### Question 4: Longest trip

**What is the length of the longest trip in the dataset in hours?**

- 22.7
- 58.2
- 90.6
- 134.5

> [!TIP]
> **My Answer:**
> The answer is **134.5**.
>
> **Approach:**
> I calculated the duration by first casting the `TIMESTAMP_NTZ` columns to standard `timestamp` (LTZ) and then to `long` (numeric seconds). Finally, I divided by 3600 to get hours.
>
> **Code Breakdown:**
> ```python
> df_yellow \
>     .withColumn('duration_hours', (
>         F.col('tpep_dropoff_datetime').cast('timestamp').cast('long') - 
>         F.col('tpep_pickup_datetime').cast('timestamp').cast('long')
>     ) / 3600) \
>     .select(F.max('duration_hours')) \
>     .show()
> ```
> 1.  **`.cast('timestamp')`**: In Spark 4.x, you cannot cast `TIMESTAMP_NTZ` directly to a number. You must first convert it to a standard `timestamp`.
> 2.  **`.cast('long')`**: Converts the timestamp to total Unix seconds.
> 3.  **`/ 3600`**: Converts the difference from seconds to hours.


### Question 5: User Interface

**Spark's User Interface which shows the application's dashboard runs on which local port?**

- 80
- 443
- 4040
- 8080

> [!TIP]
> **My Answer:**
> The answer is **4040**.
> By default, Spark starts its Web UI on port 4040. If multiple Spark sessions are running, it will increment the port (4041, 4042, etc.).



### Question 6: Least frequent pickup location zone

**Using the zone lookup data and the Yellow November 2025 data, what is the name of the LEAST frequent pickup location Zone?**

- Governor's Island/Ellis Island/Liberty Island
- Arden Heights
- Rikers Island
- Jamaica Bay

> [!TIP]
> **My Answer:**
> The answer is **Governor's Island/Ellis Island/Liberty Island**.
>
> **Approach:**
> 1.  Load the `taxi_zone_lookup.csv` file into a Spark DataFrame.
> 2.  Perform an **Inner Join** between the Yellow Taxi DataFrame and the Zones DataFrame using the Pickup Location ID (`PULocationID` and `LocationID`).
> 3.  **Group by** the `Zone` column.
> 4.  Calculate the **Count** of records for each group.
> 5.  **Order by** the count in ascending order to find the zone with the least trips.
>
> **Code Breakdown:**
> ```python
> df_zones = spark.read.option("header", "true").csv('taxi_zone_lookup.csv')
>
> df_yellow.join(df_zones, df_yellow.PULocationID == df_zones.LocationID) \
>     .groupBy('Zone') \
>     .count() \
>     .orderBy('count', ascending=True) \
>     .show()
> ```
> 1.  **`df_yellow.join(...)`**: Joins the two datasets to associate each trip with its human-readable zone name.
> 2.  **`.groupBy('Zone')`**: Aggregates all trips by their zone name.
> 3.  **`.count()`**: Counts the number of occurrences for each zone.
> 4.  **`.orderBy('count', ascending=True)`**: Sorts the results from lowest to highest count, putting the least frequent zone at the top.

