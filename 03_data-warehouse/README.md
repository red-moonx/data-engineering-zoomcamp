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

A data warehouse is a database that stores data for analysis and decision-making. It is a central repository containing different sort of data, tipically raw data, metadata and summary data. It is fed by different data sources that first report to a staging area which is then written to a data warehouse. The data warehouse can be transformed to Data Marts (smaller subsets of the data warehouse, for example, for specific departments like sales or finance) for easier analysis.




