# Module 4: Analytics Engineering

This module covers the Analytics Engineering part of the Data Engineering Zoomcamp.

## Introduction

**Data engineering** is the foundational practice of building and maintaining the infrastructure that moves raw data from disparate sources into a central warehouse, focusing on system architecture, scalability, and programming. **Analytics engineering**—a term coined in 2019 to describe tasks formerly handled by data engineers—takes over once that data has landed, applying software engineering best practices like version control, testing, and modularity to the transformation process. While the data engineer ensures data is available and moving, the analytics engineer ensures it is clean, reliable, and ready for business analysis. Though these roles are now often separated in larger organizations, they remain deeply interconnected.

## Tooling Landscape
The modern analytics engineering stack follows a clear linear path:
**Data Loading** → **Data Storing** (Cloud Data Warehouses: Snowflake, BigQuery, Redshift) → **Data Modeling** (dbt, Dataform) → **Data Presentation** (BI tools: Looker, Tableau, Google Data Studio, Mode).

---

## Data Modeling Concepts

### ETL vs. ELT
The industry has shifted from ETL to ELT to leverage the power of modern cloud warehouses.

*   **ETL (Extract, Transform, Load):** Data is transformed *before* loading. While slightly more stable for specific compliance needs, this approach often results in higher storage and compute costs and slower time-to-insight.
*   **ELT (Extract, Load, Transform):** Data is loaded in its raw form and *then* transformed within the warehouse. This provides faster, more flexible analysis and lower maintenance costs by utilizing the massive compute power of platforms like BigQuery and Snowflake.

#### Why ELT?
The ELT workflow offers several key advantages:
*   **Leverages Cloud Power**: Transformations run at scale using the warehouse's own engine.
*   **Faster Availability**: Raw data is immediately available for analysis without waiting for upstream transformations.
*   **Cost & Flexibility**: Reduces the need for expensive on-premises hardware and allows for iterative modeling as business needs evolve.
*   **Data Democratization**: Enables a self-service model where analysts can access and transform data without being bottlenecked.

### The Role of dbt
**dbt (data build tool)** serves as the transformation layer in the ELT process. It acts as the orchestrator for Analytics Engineering, enabling teams to model, test, and document data using SQL.

dbt brings software engineering best practices to data transformation:
*   **Version Control**: Tracks changes to ensure consistency and collaboration.
*   **Automation**: Schedules transformations to ensure up-to-date data.
*   **Testing**: Validates data quality and integrity automatically.

### Kimball’s Dimensional Modeling
Kimball’s Dimensional Modeling is a design approach focused on making data easy for business users to understand and fast for systems to query.

*   **Fact Tables**: Contain quantitative metrics or measurements (e.g., sale amounts, transaction counts).
*   **Dimension Tables**: Provide descriptive context (the "who, what, where") like product names, customer details, or dates.
*   **Star Schema**: A "bottom-up" design where a central fact table is surrounded by dimensions.
*   **The Grain**: In a modern ELT workflow using **dbt and BigQuery**, defining the "grain"—the specific level of detail for each row—is essential for accurate analytics.

#### Architecture of Dimensional Modeling
1.  **Stage Area**: A landing zone for raw data, accessible only to engineers to ensure integrity.
2.  **Processing Area**: The transformation layer where data moves from raw to structured models, focusing on efficiency and standards.
3.  **Presentation Area**: The final layer where cleaned, modeled data is exposed to BI tools and business users.

---

## dbt Fundamentals
**dbt** is a transformation framework that allows teams to deploy analytics code using SQL while following best practices like **modularity, portability, CI/CD, and documentation**. It essentially converts raw warehouse data into clean, ready-to-use datasets.

In a typical workflow, development happens in a **sandbox** environment, allowing for safe testing and documentation before deployment to production via CI/CD pipelines.

### How does dbt work?
dbt simplifies development by handling the "boilerplate" DDL/DML code:
*   **The `.sql` File**: Each model is a simple `.sql` file containing only a `SELECT` statement.
*   **The Compiler**: dbt compiles your code into the specific dialect of your warehouse (e.g., BigQuery) and executes it to create tables or views.

#### Example: dbt in Action
**Your Code (`total_spend.sql`):**
```sql
select
    user_id,
    sum(order_amount) as total_spent
from raw_orders
group by 1
```

**What dbt Runs in the Warehouse:**
```sql
CREATE OR REPLACE TABLE your_project.your_dataset.total_spend AS (
    select
        user_id,
        sum(order_amount) as total_spent
    from raw_orders
    group by 1
);
```

### dbt and the ADLC
The Analytics Development Lifecycle (ADLC) spans from planning and development to operations and analysis. dbt acts as the **data control plane** across these steps: design, discover, align, build, deploy, and observe.

---

## How to use dbt?
There are two primary ways to work with dbt: **dbt Core** and **dbt Cloud**.

### 1. dbt Core (Open-Source)
This is the free, open-source engine that you run locally.
*   **What it is**: A CLI tool that builds and runs dbt projects. It includes the SQL compilation logic and database adapters.
*   **How you use it**: You work in your own code editor (like VS Code) and run commands in your terminal.
*   **Your Responsibility**: You manage everything—installation, connection profiles, orchestration (Airflow/Dagster), and documentation hosting.
*   **Best for**: Developers who want full control, local development, and no subscription fees.

### 2. dbt Cloud (SaaS)
This is the managed platform designed to simplify development and deployment.
*   **What it is**: A distinct web-based IDE and orchestration platform.
*   **How you use it**: You log into a web browser. It handles Git connections, scheduling, and infrastructure.
*   **What’s included**: A built-in scheduler, managed documentation hosting, visual lineage (DAG), and collaboration features.
*   **Best for**: Teams that want a turnkey solution to start modeling immediately without managing infrastructure.

### Workshop Implementation
Depending on the database, the workshop setup varies:

*   **BigQuery (Cloud Setup)**:
    *   Developed using the **dbt Cloud IDE**.
    *   **No local installation** of dbt Core required.
    *   Workflow: `BigQuery (Data) <-> dbt Cloud (IDE)`.

*   **Postgres (Local Setup)**:
    *   Developed using a **Local IDE** (e.g., VS Code).
    *   Requires a **Local installation** of dbt Core via CLI.
    *   Uses a `profiles.yml` file to manage credentials.

### Project Implementation Options
The workshop offers two distinct paths:
1.  **Enterprise Track (dbt Cloud + BigQuery)**: Simulates a professional, cloud-native environment focusing on collaboration and managed infrastructure.
2.  **Developer Track (dbt Core + DuckDB)**: A lightweight, local experience ideal for rapid prototyping and offline development without cloud costs.

---

### The Next Generation: dbt Fusion
Released in 2025, **dbt Fusion** is a new high-performance engine written in **Rust**, replacing the legacy Python engine to provide:
*   **30x Faster Parsing**: Large projects compile in milliseconds.
*   **Pre-run Validation**: Catches SQL errors before execution.
*   **Smart Rebuilds**: Uses column-level lineage to skip unnecessary runs.
*   **Real-time IDE**: Powers the VS Code extension with live feedback.

While dbt Core remains widely used, dbt Fusion represents a significant step forward in performance and developer experience. However, ecosystem adoption is still evolving, with support for all adapters (such as DuckDB) catching up to the core engine's capabilities.

---

## 🚀 Project Setup: Google Cloud Platform & BigQuery

This section details the infrastructure setup required to run the data pipeline. We use **Google Cloud Platform (GCP)** as our cloud provider and **BigQuery** as our Data Warehouse.

### 1. Google Cloud Project Configuration
*   **Project Name:** `DE-zoomcamp-module4-luna`
*   **Project ID:** `de-zoomcamp-module4-luna`

> [!NOTE]
> Ensure the Project ID is unique and matches your configuration files exactly, as it is the primary identifier for all GCP services.

### 2. API Enablement
To allow external tools (like dbt) to interact with the project, the **BigQuery API** must be active:
1.  Search for **"BigQuery API"** in the GCP Console search bar.
2.  Click **Enable** (if not already active).

### 3. Service Account Setup (IAM)
We create a Service Account (SA) to act as a "digital worker" with specific permissions, allowing dbt to perform tasks without using a personal user login.

*   **Service Account Name:** `dbt-bigquery-SA`
*   **Roles Assigned:**
    *   `BigQuery Data User`: Grants access to read and query data.
    *   `BigQuery Job User`: Allows the account to run tasks (jobs) in BigQuery.
    *   `BigQuery User`: Provides general access to interact with the project.
    *   *(Optional)* `BigQuery Admin` for full control over BigQuery resources.

### 4. Authentication Key
To authenticate your local environment with GCP:
1.  Go to the **Keys** tab within the `dbt-bigquery-SA` service account.
2.  Select **Add Key** > **Create new key**.
3.  Choose **JSON** format and download the file.

> [!CAUTION]
> Never upload the JSON key file to GitHub. Add the filename to your `.gitignore` immediately after downloading.

---

### 📥 Data Ingestion for This Module

This module uses **yellow and green taxi trip data for 2019 and 2020**, sourced from the [DataTalksClub NYC TLC Data repository](https://github.com/DataTalksClub/nyc-tlc-data/releases). The ingestion pipeline downloads all 48 files and uploads them to a **Google Cloud Storage (GCS)** bucket, where they serve as the raw data source for BigQuery external tables.

#### What Gets Loaded

| Parameter | Value |
|---|---|
| **GCS Bucket** | `dezoomcamp_hw4_lunazea_2026` |
| **Colors** | Yellow, Green |
| **Years** | 2019, 2020 |
| **Months** | January – December (12 months each) |
| **Total Files** | 48 (2 colors × 2 years × 12 months) |
| **File Format** | `.csv.gz` (compressed CSV) |

#### How It Works

The [`load_taxi_data.py`](load_taxi_data.py) script handles the full pipeline:

1. **Authenticates** with GCP using the service account JSON key.
2. **Verifies** the GCS bucket exists and is accessible.
3. **Downloads** all files in parallel (4 threads) from the DataTalksClub GitHub releases.
4. **Uploads** each file to GCS with chunked transfer and verifies every upload before deleting the local copy.

The script is packaged in a Docker container to ensure a consistent, reproducible environment regardless of local Python setup.

#### GCS Bucket Setup

The bucket must be created **before** running the script, since the service account (`dbt-bigquery-sa`) only has object-level permissions — not project-level bucket creation rights. We created it manually via the terminal:

```bash
gcloud storage buckets create gs://dezoomcamp_hw4_lunazea_2026 \
  --project=de-zoomcamp-module4-luna \
  --location=US
```

Then granted the service account access to the bucket:

```bash
gcloud storage buckets add-iam-policy-binding gs://dezoomcamp_hw4_lunazea_2026 \
  --member="serviceAccount:dbt-bigquery-sa@de-zoomcamp-module4-luna.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

> [!NOTE]
> We also simplified the `create_bucket()` function in the script to remove a `list_buckets()` call that required project-wide IAM permissions. It now simply checks if the bucket is accessible with `get_bucket()` — a cleaner and less privileged approach.

#### Running the Pipeline

```bash
# Build the Docker image
docker build -t taxi-data-loader .

# Run the container
docker run --name taxi-data-loader taxi-data-loader

# Clean up after a previous run (if re-running)
docker rm taxi-data-loader
```

Once complete, all 48 files will be available at `gs://dezoomcamp_hw4_lunazea_2026/` and ready to be referenced as **BigQuery external tables**.

---

### 🗄️ BigQuery Dataset & External Tables

With the raw files in GCS, we create a **BigQuery dataset** and **external tables** that point directly to them — the same pattern used in Module 3. dbt will then use these external tables as its raw source layer.

#### Step 1: Create the Dataset

In the BigQuery Console, create a dataset named `nytaxi` in your project. Or via terminal:

```bash
bq mk --dataset de-zoomcamp-module4-luna:nytaxi
```

#### Step 2: Create External Tables

Run the following SQL in the BigQuery Console:

```sql
-- External table for yellow taxi (2019 & 2020)
CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-module4-luna.nytaxi.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = [
    'gs://dezoomcamp_hw4_lunazea_2026/yellow_tripdata_2019-*.csv.gz',
    'gs://dezoomcamp_hw4_lunazea_2026/yellow_tripdata_2020-*.csv.gz'
  ]
);

-- External table for green taxi (2019 & 2020)
CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-module4-luna.nytaxi.external_green_tripdata`
OPTIONS (
  format = 'CSV',
  uris = [
    'gs://dezoomcamp_hw4_lunazea_2026/green_tripdata_2019-*.csv.gz',
    'gs://dezoomcamp_hw4_lunazea_2026/green_tripdata_2020-*.csv.gz'
  ]
);
```

> [!NOTE]
> BigQuery reads `.csv.gz` files natively — no decompression needed. The `*` wildcard matches all monthly files for each year.

Unlike Module 3, we do **not** create partitioned or clustered native tables here — dbt will handle all further transformations using these external tables as the raw source.

---

## 🛠️ dbt Cloud Setup

### 1. Create a Developer Account
Sign up for a free **dbt Cloud Developer account** at [cloud.getdbt.com](https://cloud.getdbt.com). The developer tier is sufficient for this module.

### 2. Connect to BigQuery
In the dbt Cloud account settings, create a new **BigQuery connection**:
- Upload the service account JSON key (`de-zoomcamp-module4-luna-65a6fedc7780.json`) as the auth credentials.
- Set the project to `de-zoomcamp-module4-luna` and the dataset to `nytaxi`.
- Test the connection to verify it succeeds before moving on.

### 3. Integrate GitHub
Under account settings, connect your **GitHub account** to dbt Cloud. This allows dbt to pull and push code directly from your repositories.

### 4. Set Up a Project in dbt Studio
Navigate to **dbt Studio** (the web IDE) and create a new project:
1. **Add the BigQuery connection** configured above.
2. Fill in the required fields: auth credentials, a unique project name, dataset, etc.
3. **Test the connection** to confirm everything is wired up correctly.

### 5. Choose a Repository
After the connection test, select where dbt will store your project code:

| Option | When to use |
|---|---|
| **GitHub** (recommended) | Production setups — full version control via your own repo |
| **Managed** *(used here)* | Learning/exploration — dbt Cloud hosts the repo for you |

> [!NOTE]
> For this module we selected **Managed** for simplicity. In a real project, always use a GitHub-connected repository for proper version control and CI/CD.

### 6. Initialize the dbt project
It creates the entire structure for the project. After, I created a new brach with my name and commit. 

