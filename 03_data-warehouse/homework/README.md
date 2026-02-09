# Module 3 Homework: Data Warehousing & BigQuery

In this homework we'll practice working with BigQuery and Google Cloud Storage.

When submitting your homework, you will also need to include
a link to your GitHub repository or other public code-hosting
site.

This repository should contain the code for solving the homework.

When your solution has SQL or shell commands and not code
(e.g. python files) file format, include them directly in
the README file of your repository.

## Data

For this homework we will be using the Yellow Taxi Trip Records for January 2024 - June 2024 (not the entire year of data).

Parquet Files are available from the New York City Taxi Data found here:

https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## Loading the data

You can use the following scripts to load the data into your GCS bucket:

- Python script: [load_yellow_taxi_data.py](./load_yellow_taxi_data.py)
- Jupyter notebook with DLT: [DLT_upload_to_GCP.ipynb](./DLT_upload_to_GCP.ipynb)

You will need to generate a Service Account with GCS Admin privileges or be authenticated with the Google SDK, and update the bucket name in the script.

If you are using orchestration tools such as Kestra, Mage, Airflow, or Prefect, do not load the data into BigQuery using the orchestrator.

Make sure that all 6 files show in your GCS bucket before beginning.

Note: You will need to use the PARQUET option when creating an external table.

> [!TIP] 
> **My Answer:** 
> 
> **Approach used:**
> To load the data, I run the `load_yellow_taxi_data.py` script. 
> To ensure a consistent environment and manage dependencies (using `uv`), I containerized the script using Docker (Dockerfile in the same directory).
> 
> **Steps taken:**
> 1. As I'm reusing the Project from Module 2, I only needed to create a new bucket (variable name included in `load_yellow_taxi_data.py`).
> 2. I also placed the Google Cloud Service Account key (`gcs.json`) in the directory.
> 3. Built and ran the Docker container with the following command:
> 
> ```bash
> docker build -t taxi-ingest:uv . 
> docker run -v $(pwd)/gcs.json:/app/gcs.json -it taxi-> ingest:uv
> ```
> This successfully uploaded the parquet files to the bucket `dezoomcamp_hw3_lunazea_2026`.

## BigQuery Setup
Create an external table using the Yellow Taxi Trip Records. 
Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table). 

> [!TIP] 
> **My Answer:** 
> First, I create the dataset:
> ```sql
> CREATE SCHEMA IF NOT EXISTS `dezoomcamp_module3`;
> ```
> 
> **Create an external table using the Yellow Taxi Trip Records.**
> ```sql
> CREATE OR REPLACE EXTERNAL TABLE `dezoomcamp_module3.yellow_tripdata_2024_ext`
> OPTIONS (
>   format = 'PARQUET',
>   uris = ['gs://dezoomcamp_hw3_lunazea_2026/yellow_tripdata_2024-*.parquet']
> );
> ```
> 
> **Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table).**
> ```sql
> CREATE OR REPLACE TABLE `dezoomcamp_module3.yellow_tripdata_2024` AS
> SELECT * FROM `dezoomcamp_module3.yellow_tripdata_2024_ext`;

### 1. Counting records
**What is the count of records for the 2024 Yellow Taxi Data?**
- 65,623
- 840,402
- 20,332,093
- 85,431,289

> [!TIP]
> **My Answer:** 
> ```sql
> SELECT COUNT(*) FROM `dezoomcamp_module3.yellow_tripdata_2024`;
> ```
> The answer is 20,332,093


### 2. Data read estimation
**Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?**

18.82 MB for the External Table and 47.60 MB for the Materialized Table
0 MB for the External Table and 155.12 MB for the Materialized Table
2.14 GB for the External Table and 0MB for the Materialized Table
0 MB for the External Table and 0MB for the Materialized Table
 
> [!TIP]
> **My Answer:** 
> The SQL questies are:
> 
> For the external table:
> ```sql
> SELECT COUNT(DISTINCT PULocationID) FROM `dezoomcamp_module3.yellow_tripdata_2024_ext`;
> ```
> 
> For the materialized table:
> ```sql
> SELECT COUNT(DISTINCT PULocationID) FROM `dezoomcamp_module3.yellow_tripdata_2024`;
> ``` 
> The answer is: 0 MB for the External Table and 155.12 MB for the Materialized Table


### 3. Understanding columnar storage
**Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?**

- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.
- BigQuery duplicates data across multiple storage partitions, so selecting two columns instead of one requires scanning the table twice, doubling the estimated bytes processed.
- BigQuery automatically caches the first queried column, so adding a second column increases processing time but does not affect the estimated bytes scanned.
- When selecting multiple columns, BigQuery performs an implicit join operation between them, increasing the estimated bytes processed

> [!TIP]
> **My Answer:** 
> The SQL queries requested are:
> ```sql
> SELECT PULocationID FROM `dezoomcamp_module3.yellow_tripdata_2024`;
> ``` 
> and:
> ```sql
> SELECT PULocationID, DOLocationID FROM `dezoomcamp_module3.yellow_tripdata_2024`;
> ``` 
> First query processes 155.12 MB, and the second one processes 310.24 MB
> 
> BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.


### 4. Counting zero fare trips
**How many records have a fare_amount of 0?**

- 128,210
- 546,578
- 20,188,016
- 8,333

> [!TIP]
> **My Answer:** 
> ```sql
> SELECT COUNT(*) FROM `dezoomcamp_module3.yellow_tripdata_2024` WHERE fare_amount = 0;
> ```
> Answer is: 8,333

### 5. Partitioning and clustering
**What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)**

- Partition by tpep_dropoff_datetime and Cluster on VendorID
- Cluster on by tpep_dropoff_datetime and Cluster on VendorID
- Cluster on tpep_dropoff_datetime Partition by VendorID
- Partition by tpep_dropoff_datetime and Partition by VendorID

> [!TIP]
> **My Answer:** 
> It is better to partition by the column we usually base the filter on:
> Partition by tpep_dropoff_datetime and Cluster on VendorID
> 
>```sql
>CREATE OR REPLACE TABLE `dezoomcamp_module3.yellow_tripdata_2024_part_clust`
>PARTITION BY DATE(tpep_dropoff_datetime)
>CLUSTER BY VendorID AS (
>  SELECT * FROM `dezoomcamp_module3.yellow_tripdata_2024`
>);
>```



### 6. Partition benefits

**Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime 2024-03-01 and 2024-03-15 (inclusive)**

**Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values?**

**Choose the answer which most closely matches.**

- 12.47 MB for non-partitioned table and 326.42 MB for the partitioned table
- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table
- 5.87 MB for non-partitioned table and 0 MB for the partitioned table
- 310.31 MB for non-partitioned table and 285.64 MB for the partitioned table

> [!TIP]
> **My Answer:** 
> Using the non-partitioned table (310.24 MB data processed):
>```sql
> SELECT DISTINCT VendorID 
> FROM `dezoomcamp_module3.yellow_tripdata_2024`
> WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15'
>```
>
> Using the partitioned table (26.84 MB MB data processed):
>```sql
>SELECT DISTINCT VendorID 
>FROM `dezoomcamp_module3.yellow_tripdata_2024_part_clust`
>WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15'
>```
>
> The correct answer is: 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table


### 7. External table storage
**Where is the data stored in the External Table you created?**

- Big Query
- Container Registry
- GCP Bucket
- Big Table


> [!TIP]
> **My Answer:** 
> The external table is stored in the GCP Bucket. Unlike native tables, BigQuery does not ingest or "own" the raw data; it simply maintains a metadata link that points to the file's URI (such as a Parquet or CSV file path).



### 8. Clustering best practices
**It is best practice in Big Query to always cluster your data:**

- True
- False

> [!TIP]
> **My Answer:**
> False, it depends on the specific query patterns and the size of the dataset. Generally, clustering is a best practice for large tables (> 1 GB) where queries frequently filter or aggregate using specific columns. However, it is better to skip clustering on small datasets, when query patterns are highly varied rather than targeting primary columns, or when the data has high churn.



### 9. Understanding table scans

**No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?**

> [!TIP]
> **My Answer:** 
> 0 Bytes. There are a few reasons:
> 1. **Metadata vs data scans:**
> For native tables, BigQuery constantly maintains a count of the total number of rows. When we ask for a simple count(*), BigQuery’s optimizer doesn't bother looking at the actual data rows; it simply pulls the number from the table's metadata.
> 2. **Columnar storage:**
> BigQuery uses a columnar format (Capacitor). In a standard query, you are charged based on the amount of data in the columns you select. Because count(*) doesn't require reading any specific column values to give you a total tally, there is no data "processed" in the traditional sense.
> 3. **Materialized vs external table:**
> For external files (CSV, Parquet), BigQuery doesn't "own" the metadata, so it actually has to scan the files to count the rows, leading to a non-zero byte estimate.


