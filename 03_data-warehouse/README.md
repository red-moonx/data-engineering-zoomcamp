# Module 3: Data Warehouse

Here are my notes for Module 3 of the Data Engineering Zoomcamp course.

## 1. Introduction to Data Warehouse and Bigquery

In this module, we explore the concepts of Data Warehousing and learn how to use Google BigQuery for efficient data storage and analysis.

### OLAP vs OLTP

OLAP and OLTP are two primary data processing systems, but they serve different purposes:

| Feature | OLTP (Online Transaction Processing) | OLAP (Online Analytical Processing) |
| :--- | :--- | :--- |
| **Focus** | Day-to-day operations | Data analysis and decision making |
| **Operations** | Short, fast updates | Long-running, complex read queries |
| **Data Volume** | Small transactions (GBs) | Massive datasets (TBs/PBs) |
| **Data Structure** | Highly Normalized (3NF) | Denormalized (Star/Snowflake Schema) |
| **Access Pattern** | Row-oriented | Column-oriented |
| **Latency** | Low latency (millis) | Higher latency (seconds/minutes) |

### Data Warehouse

A data warehouse is a database that stores data for analysis and decision-making. It is a central repository containing different sort of data, tipically raw data, metadata and summary data. It is fed by different data sources that first report to a staging area which is then written to a data warehouse. The data warehouse can be transformed to Data Marts (smaller subsets of the data warehouse, for example: purchasing, sales, inventory...) for easier analysis. A data warehouse provides all these possibilities of accessing raw data, summary data or data marts. 

### Bigquery

BigQuery is a serverless, highly scalable, and cost-effective cloud data warehouse. It allows you to analyze large datasets using SQL queries, and it integrates with other Google Cloud services. BigQuery is a columnar database, which means that it stores data in columns rather than rows. This makes it very efficient for analytical queries, as it only needs to read the columns that are needed for the query. It has built-in functions such as machine learning (via de SQL interface), geospatial analysis or business intelligence. It maximizes flexibility by separating the compute engine (data analysis) from the storage engine. It also huge library of public datasets

BigQuery pricing modes are on-demand (pay per TB of data processed) or flat rate (pay for a fixed number of slots/compute capacity). Flat rate only makes sense when processing way above 200 terabytes of data. 

#### Other GCP components related to BigQuery

- **External Table**: A table definition that points to data stored outside of BigQuery (e.g., in GCS), allowing you to query it without loading the data.
- **Project**: The logical organizer and billing unit for all your resources (BigQuery datasets, Storage buckets, compute instances).
- **Bucket**: A container in Google Cloud Storage (GCS) where you store files (objects).
- **Service Account**: A special account for non-human users (like your Kestra workflow) with specific permissions to act on resources.
- **Cloud Storage URI (`gs://`)**: A path pointing to a file or folder in a GCS bucket (e.g., `gs://bucket/file.csv`).

## 2. BigQuery: Partitioning and Clustering

- **Partitioning**: Splits a table into smaller segments based on a specific column (usually date or time), saving space and costs, and speeding up queries. 
- **Clustering**: Reorders data within those partitions based on other columns (like `tag` or `customer_id`), keeping related data close together for faster retrieval. 

Important considerations:
- When using time for partinioting the default is daily, but it can be modified to hourly, monthly, yearly, etc. (with a limit of partitions being 4,000). Clustering is not limited in the number of columns (up to 4).
- It is not recommended to partition and clustering a table < 1 Gb size, it doesn't improve performance but maintaining it will increase costs.
- When to use partioning, when clustering, and when both? For that we need to look at their properties:

**Partitioning**
- **Definition**: Splits your table into "segments" based on a single column (usually a Date or an Integer).
- **Cost known upfront**: Because the data is separated into physical "buckets", BigQuery knows exactly how much data to scan.
- **Partition-level management**: Easily delete or replace specific partitions (e.g., a single day) without touching the rest.
- **Filter on a single column**: Ideal when you frequently filter by that specific column.

**Clustering**
- **Definition**: Sorts data within partitions based on one or more columns (up to 4).
- **Cost benefit unknown**: You'll save money, but exact estimates aren't available before execution.
- **High Cardinality & Granularity**: Perfect for columns with many unique values (like `email`) or finding specific data within a partition (e.g., "Users in Berlin" inside "January").
- **Multiple columns**: Great if you often filter by different combinations (e.g., `country` AND `category`).

**When to choose Clustering over Partitioning**
- **Small partitions**: When partitioning would result in small amounts of data per partition (< 1 GB).
- **High cardinality**: When you would exceed the limit of partitions (max 4,000) or have too many unique values.
- **Frequent updates**: When your pipeline modifies the majority of partitions frequently (e.g., every few minutes).

### BigQuery best practices

- **Cost Reduction**:
    - **Avoid `SELECT *`**: BigQuery is a columnar store, so you are charged for every column you select. Query only the specific columns you need.
    - **Price your queries**: Use the UI or API (dry run) to see the estimated bytes processed *before* you run the query.
    - **Use clustered or partitioned tables**: Reading only the necessary partitions/clusters drastically reduces the data scanned and the cost.
    - **Use streaming inserts with caution**: Streaming data (`insertAll`) incurs extra costs. If possible, load data in bulk (Load Jobs) which is free.
    - **Materialize query results**: If you run a complex query often, save the result to a table (materialization) so you don't recompute it every time.





