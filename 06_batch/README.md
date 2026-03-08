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

### 1.2. Technologies Used
*   **Python Scripts**: Primarily used for data ingestion and light orchestration.
*   **SQL**: Used for data transformations (Dbt, BigQuery).
*   **Spark**: Used for **large-scale data processing** and heavy-duty transformations that benefit from parallel computation.
*   **Orchestration**: A typical workflow involves tools like **Airflow** to manage the pipeline dependencies and scheduling.


## 2. Introduction to Apache Spark

### 2.1. What is Apache Spark?
Apache Spark is a powerful, open-source **distributed computing engine** designed for large-scale data processing. It operates across a **cluster** of machines to process data stored in architectures ranging from **Data Lakes** to **Data Warehouses**.

**Key Features:**
*   **Multi-language Support**: While written in **Scala**, it provides high-level APIs for **Python (PySpark)**, **Java**, and **R**.
*   **Unified Engine**: PySpark is versatile, supporting both **Batch Processing** and **Stream Processing**.
*   **Performance**: Uses in-memory processing to stay significantly faster than traditional MapReduce jobs.

### 2.2. When and Why to Use Spark?
Spark is typically used when data resides in a **Data Lake** (e.g., S3 or GCS) in formats like **Parquet**. Spark extracts the data, processes it, and often writes the results back to the Data Lake.

**Decision Framework: SQL vs. Spark**
*   **Rule of Thumb**: If you can express a job in **SQL**, use SQL (BigQuery, Snowflake, Presto, Athena). It is generally easier to maintain and optimize.
*   **Use Spark When**:
    *   The logic is too complex for standard SQL.
    *   You need specialized data processing (e.g., graph processing or advanced text manipulation).
    *   **Machine Learning**: Spark is the industry standard for training and applying models at scale.

### 2.3. Typical Workflows
A standard enterprise data pipeline often looks like this:
1.  **Ingestion**: Raw data is landed in a **Data Lake**.
2.  **SQL Layer**: Initial transformations (joins, filtering) are performed using SQL.
3.  **Spark Layer**: Complex business logic or ML-specific preparations are handled via Spark.
4.  **Machine Learning**: Models are trained on the processed data.
5.  **Inference**: Spark is used to apply a trained model to massive datasets (Inference), sending results back to the Data Lake and finally into a **Data Warehouse** for reporting.


## 3. Installation 
We are using **GitHub Codespaces** running **Ubuntu 24.04.3 LTS (Noble Numbat)**. Spark can be installed directly using Python via the `pyspark` package, which bundles the Spark binaries.

### 3.1. Prerequisites
- **Java**: Java 25 is pre-installed at `/usr/local/sdkman/candidates/java/current`.
- **uv**: The modern Python package manager `uv` is recommended for managing dependencies.

### 3.2. Installation Steps
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

### 3.3. Verification
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

### 3.4. Test Results & Explanation
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


### 3.5. Jupyter Notebook Setup
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
 
+## 4. Initial Test: 03_test.ipynb
+The `03_test.ipynb` notebook serves as a "Hello World" for PySpark in this module. It verifies the environment by performing the following operations:
+
+1.  **Environment Check**: Confirms that Python can locate the `pyspark` libraries.
+2.  **Spark Session Initialization**: Starts a local Spark cluster using `.master("local[*]")`, which utilizes all available CPU cores for parallel processing.
+3.  **Data Ingestion**: Downloads the NYC Taxi Zone Lookup dataset (CSV) and loads it into a Spark DataFrame.
+4.  **DataFrame Operations**: Uses `df.show()` to display the first 20 rows of the dataset, confirming the distributed computing engine is functioning.
+5.  **Format Conversion**: Writes the DataFrame to **Parquet** format. This is a critical data engineering step, as Parquet is a columnar storage format optimized for Spark, providing better compression and performance than CSV.
+
+Successfully running this notebook confirms that the Spark cluster is healthy and the environment is ready for large-scale data processing.

