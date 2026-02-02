# Module 2 – Data Orchestration

Here are my notes for Module 2 of the Data Engineering Zoomcamp course.

## 0. Recap of key concepts from Module 1

### Key Concepts

#### Containerization (Docker)
- Containers package an application and its dependencies into an isolated runtime.
- Containers are **ephemeral** by design: they can be stopped, removed, and recreated at any time.

#### Images vs Containers
- **Docker Image**: a read-only blueprint (OS + runtime + dependencies + code)
- **Docker Container**: a running instance of an image

#### Volumes (Persistence)
- Containers should not own state.
- **Docker volumes** store persistent data outside containers.
- Volumes survive container restarts and removals.

> [!NOTE]
> Containers run logic. Volumes store state.

---

## 1. Introduction to Data Orchestration

**Data orchestration** is the practice of coordinating, scheduling, and monitoring data workflows so tasks run in the correct order, at the right time, and with proper dependency management.

### Key ideas:
- Orchestration ≠ data processing
- Orchestrators manage **execution flow**, retries, failures, and dependencies
- Tasks themselves should be **stateless and replaceable**

In this module, the focus is on **ETL (Extract, Transform, Load)** pipelines and how to orchestrate them reliably.

---

## 2. Workflow Orchestration with Kestra

We introduce **Kestra** as the orchestration engine.

### Why Kestra?
- Workflow orchestration platform
- Supports **code, no-code, and AI-assisted workflows**
- **Language-agnostic**: tasks can be implemented in different languages
- Designed for data pipelines and automation

Kestra acts as the **conductor**, not the worker:
- It schedules tasks
- It tracks state and execution
- It does not replace the tools that actually process data

### Kestra Infrastructure Setup

To integrate orchestration, we extend the existing Docker Compose setup from Module 1 by adding **two new services**.

#### 1. Kestra Metadata Database (`kestra_postgres`)

```yaml
kestra_postgres:
  image: postgres:18
  volumes:
    - kestra_postgres_data:/var/lib/postgresql
  environment:
    POSTGRES_DB: kestra
    POSTGRES_USER: kestra
    POSTGRES_PASSWORD: k3str4
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -u $${POSTGRES_USER}"]
    interval: 30s
    timeout: 10s
    retries: 10
```

**Purpose:**
- Stores Kestra's internal state:
  - workflow definitions
  - execution metadata
  - task status
  - queues

> [!IMPORTANT]
> This database is **not user data** — it is **orchestration metadata**.

#### 2. Kestra Server (`kestra`)

```yaml
kestra:
  image: kestra/kestra:v1.1
  pull_policy: always
  user: "root"
  command: server standalone
  volumes:
    - kestra_data:/app/storage
    - /var/run/docker.sock:/var/run/docker.sock
    - /tmp/kestra-wd:/tmp/kestra-wd
  environment:
    KESTRA_CONFIGURATION: |
      datasources:
        postgres:
          url: jdbc:postgresql://kestra_postgres:5432/kestra
          driverClassName: org.postgresql.Driver
          username: kestra
          password: k3str4
      kestra:
        server:
          basicAuth:
            username: "admin@kestra.io"
            password: Admin1234!
        repository:
          type: postgres
        storage:
          type: local
          local:
            basePath: "/app/storage"
        queue:
          type: postgres
        tasks:
          tmpDir:
            path: /tmp/kestra-wd/tmp
      url: http://localhost:8080/
  ports:
    - "8080:8080"
    - "8081:8081"
  depends_on:
    kestra_postgres:
      condition: service_started
```

**Purpose:**
- Runs the Kestra orchestration engine
- Exposes a web UI on `http://localhost:8080`
- Connects to its own PostgreSQL metadata database
- Uses volumes for:
  - workflow storage
  - execution artifacts
  - temporary task working directories

> [!TIP]
> The Docker socket is mounted to allow Kestra to orchestrate containerized tasks in development.

#### 3. Named Volumes

To ensure data persistence for our new services, we define named volumes in the `volumes` section of our `docker-compose.yaml`.

```yaml
volumes:
  kestra_postgres_data:
    driver: local
  kestra_data:
    driver: local
```

### Architecture So Far (Mental Model)

- **PostgreSQL (`pgdatabase`)** -> stores application data (e.g. ny_taxi)
- **pgAdmin** -> UI for interacting with PostgreSQL
- **Kestra PostgreSQL (`kestra_postgres`)** -> stores orchestration metadata
- **Kestra Server** -> orchestrates ETL workflows, schedules tasks, tracks execution state

**Each service:**
- owns its own state
- uses its own volume
- can be restarted independently

### Key Takeaways So Far

- Orchestration tools manage **control flow**, not data processing
- Containers are disposable; volumes are durable
- Ports exist to bridge **host <-> container**, not container <-> container
- Real-world data systems separate:
  - **execution**
  - **state**
  - **orchestration**
- Docker Compose is a first step toward understanding production orchestration

---

### Status Update: Infrastructure Verified

After running `docker compose up`, all services are working correctly. I can successfully login to the Kestra UI and I'm ready to build my first workflow.

#### The Four-Container Architecture:
1.  **`kestra`**: The server/brain that schedules and runs your workflows.
2.  **`kestra_postgres`**: Stores **Metadata** (YAML flows, execution history, logs). It's the "filing system" for Kestra.
3.  **`pgdatabase`**: Stores your **Application Data** (the New York taxi data). It's the "warehouse".
4.  **`pgadmin`**: A management UI to look inside `pgdatabase`.

#### Why two separate Postgres instances?
We use two databases to achieve **Separation of Concerns**:
*   **Isolation**: If `pgdatabase` crashes while processing heavy data, Kestra stays alive because its metadata in `kestra_postgres` is separate.
*   **Mental Model**: In production, we separate "Information about the system" (Metadata) from the "System's actual Information" (Data).

![Kestra Dashboard](file:///workspaces/data-engineering-zoomcamp/02_data-orchestration/kestra-dashboard.png)

---

### Kestra Concepts and Flows

In this section, we dive into the core concepts of Kestra that allow us to build robust data pipelines.

To explore the course examples, I will copy the `flows` folder from the course's repository (from the 2026 Cohort). 

#### Core Concepts

*   **ID and Namespace**: Every workflow has a unique ID and a namespace (which groups related flows). **Note**: Once you save a flow, you cannot change its ID or namespace.
*   **Tasks**: The modifiable building blocks of a workflow.
    *   Each task has an **ID** and a **Type** (e.g., `log`, `return`, `sleep`).
    *   Tasks have specific **Properties** (e.g., a `sleep` task has a `duration`). You can find these details in the official documentation or examples.
*   **Inputs**: Values provided when a workflow is executed.
    *   They have an **ID**, **Type**, and optional **Default Value**.
    *   Inputs can be referenced within tasks using expressions (e.g., `{{ inputs.my_input }}`).
*   **Variables**: Similar to inputs, but defined within the flow for values used multiple times. They help keep your YAML DRY (Don't Repeat Yourself).
*   **Outputs**: Tasks generate data (outputs) that can be used as input for subsequent tasks in the same flow.
*   **Triggers**: Mechanisms to start a flow automatically based on events like a schedule or a webhook.
*   **Concurrency**: Features to manage how many instances of a flow or task can run simultaneously, preventing resource overload.

Once the workflow has run, we can explore several features:
*   **Gantt Chart**: A real-time visual overview of the workflow execution, showing the timing and duration of each task.
*   **Logs**: Detailed logs for each task, showing inputs, outputs, and any errors.
*   **Metrics**: Metrics about the workflow execution, such as duration, success rate, and resource usage.

---

### Orchestrating Python Code

Kestra can run Python scripts as part of a workflow. We are working with the `02_python.yaml` example.

There are two primary ways to execute Python in Kestra:

#### 1. The Script Task (`io.kestra.plugin.scripts.python.Script`)
This is the approach used in `02_python.yaml`.
*   **Best for**: Short snippets, quick data transformations, or logic that can be written directly in the YAML flow.
*   **Pros**: Entire logic is visible in one file; easy to reference flow inputs and variables.
*   **Cons**: Can make the YAML file very long and harder to maintain if the script grows complex.

#### 2. The Commands Task (`io.kestra.plugin.scripts.python.Commands`)
*   **Best for**: Longer scripts, multi-file projects, or when you want to keep your workflow definition clean.
*   **How it works**: You store your logic in external `.py` files and use the `Commands` task to execute them.
*   **Pros**: Keeps the YAML definition focused on the high-level orchestration; allows for better code organization and version control of the Python logic itself.

#### Important takeaways:
*   **Docker Runner**: Kestra runs the Python script inside a dedicated Docker container (`python:slim`), ensuring a consistent environment.
*   **Dependency Management**: It uses uv under the hood to manage dependencies (like `requests` and `kestra`)in our case, using the `dependencies` property.
*   **Kestra Library**: By importing `from kestra import Kestra`, the script can send outputs and metrics back to the Kestra UI.

---

## 3. ETL data pipeline with Kestra

In this section, we move beyond simple scripts to a full **ETL (Extract, Transform, Load)** pipeline. We use the flow `03_getting_started_data_pipeline.yaml` as our example.

This workflow demonstrates how Kestra manages the data flow between different types of tasks:

*   **Extract (`extract`)**: Uses the `http.Download` plugin to fetch a JSON file from an external API (`dummyjson.com`).
    *   **Output**: The task produces an internal storage **URI** (e.g., `kestra://...`). This URI is a pointer to the data stored in Kestra's internal backend, not the data itself.
*   **Transform (`transform`)**: A Python script task that filters the raw JSON.
    *   **Input**: It uses the `inputFiles` property to "mount" the URI from the extract task as a local file named `data.json`.
    *   **Logic**: It filters the products based on an input parameter `columns_to_keep`.
    *   **Output**: It saves the result as `products.json`, which is then captured as an output artifact.
*   **Query (`query`)**: Uses the **DuckDB** plugin to analyze the transformed data.
    *   **Input**: Similar to the transform task, it mounts the `products.json` output from the previous step.
    *   **Logic**: It runs a SQL query to calculate the average price per brand.
    *   **Output**: The results are stored and can be viewed directly in the Kestra UI.

### Load data into Postgres with ETL

Now we are building an ETL pipeline using a PostgreSQL database. The workflow `04_postgres_taxi.yaml` handles the logic for a single data segment (one taxi type for one month), but we can use Kestra's orchestration features to handle the entire dataset.

#### The steps we are taking:

1.  **Use the NY taxi data**: As we did in Module 1, the data is split into months. 
    *   **Single vs Multiple**: While the `extract` task in this specific flow downloads **one** CSV file at a time (based on your inputs), Kestra allows us to automate the processing of multiple files through **Backfilling**.
2.  **Parameterization (Inputs)**:
    *   Before we start, we need to know which month we are processing, whether it's yellow or green taxi data, etc. This is where **Inputs** come in handy.
    *   Our inputs are `taxi` type, `year`, and `month`. We can change these values when we trigger the flow.
    *   Following the inputs, we are creating variables that will store elements of the workflow that we will reference in several tasks (such as filename, staging or final table, etc.). Because the green and yellow taxi datasets have different schemas, we need to create different tables for each.

3.  **Set Label (`set_label`)**:
    *   One of the first steps is to set a **Label** for the execution.
    *   This ensures that in the Execution UI, we can immediately see which file (e.g., `yellow_tripdata_2021-01.csv`) is being processed, rather than just seeing a generic flow ID.

4.  **Extract (`extract`)**:
    *   Extraction is the first step of the ETL pipeline. In this case, we are extracting the data from the DataTalksClub github repository.
    *   Uses a **Shell Command** (`wget`) to download the compressed `.csv.gz` file.
    *   The file is piped into `gunzip` and stored in the Kestra internal working directory.
5.  **Loading with Staging Tables**:
    *   **Create Tables**: Here, we start adding some PostgreSQL tasks. We create both the final destination table and a temporary `staging_table`. First, only the column titles (the ones present in the origin table, and also some new columns like a unique ID - to ensure no duplications- and filename).
    *   **Truncate Staging**: Clears the staging table before every run.
    *   **High-Speed Ingestion (`CopyIn`)**: Uses the `jdbc.postgresql.CopyIn` plugin for maximum performance.
    *   > **Note on Performance**: We use two different Postgres task types:
        *   `Queries`: For standard SQL logic (DDL, updates, merges).
        *   `CopyIn`: Specifically for bulk data loading. It uses the specific PostgreSQL `COPY FROM STDIN` command to stream binary/text data directly, which is significantly faster than running thousands of `INSERT` statements.
6.  **Transformations (Enrichment & Deduplication)**:
    *   Once the data is in the staging table, we run a **SQL `UPDATE`** query to add two new columns that weren't in the original CSV:
        1.  **`unique_row_id`**: Generated by calculating an **MD5 hash** of key columns.
        2.  **`filename`**: We add the source filename for traceability.
        > **Why Update separately?** We cannot add these columns during the `CopyIn` step because `COPY` requires the input CSV structure to match the target columns exactly. Since our raw CSV lacks these fields, we load the raw data first, then use Postgres's efficient engine to populate the new columns.
    *   **MERGE INTO**: Finally, we use these IDs to merge data into the main table, ensuring **idempotency** (we only insert records that don't already exist).
7.  **Cleanup (`purge_files`)**:
    *   Removes temporary files to save execution storage space.
8.  **Plugin Configuration (DRY Principle)**:
    *   Instead of repeating the database credentials (`url`, `username`, `password`) in every single task, we use the `pluginDefaults` section at the end of the flow.
    *   This global configuration automatically applies connection details to any task matching the specified type (e.g., `io.kestra.plugin.jdbc.postgresql`), keeping the code clean and maintainable.

### Workflow execution
I have successfully run the `04_postgres_taxi` workflow in Kestra, with the following inputs: `taxi=green`, `year=2019`, `month=01`. The pipeline completed all steps, from initializing the labels to merging the data into Postgres.

![Green Taxi Execution](file:///workspaces/data-engineering-zoomcamp/02_data-orchestration/green_taxi_execution.png)  


---

### Verifying data in pgAdmin

Now that the pipeline has run successfully, we can inspect the data in the database using pgAdmin.
After connecting,we see `green_tripdata` (the final table) and `green_tripdata_staging`(temporal table for each combination of taxi type, year and month).
*   **Final Table**: Accumulates data. After running for 2019-01 and then 2019-02, the row count grows (e.g., from ~630k to ~1.2m).
*   **Staging Table**: Transient. It holds only the current batch relative to the specific execution and is **truncated** (cleared) at the start of every new run, so you might find it empty or containing only the latest processed file.

1.  **Access pgAdmin**: Go to `http://localhost:8085`.
2.  **Login**:
    *   **Email**: `admin@admin.com`
    *   **Password**: `root`
3.  **Register a New Server**:
    *   Right-click `Servers` -> `Register` -> `Server...`.
    *   **General Tab**:
        *   **Name**: `Taxi Data` (or any name you prefer).
    *   **Connection Tab**:
        *   **Host name/address**: `pgdatabase` (this is the docker service name).
        *   **Port**: `5432`
        *   **Maintenance database**: `ny_taxi`
        *   **Username**: `root`
        *   **Password**: `root`
    *   Click `Save`.
4.  **Inspect Data**:
    *   Navigate to `Servers` -> `Taxi Data` -> `Databases` -> `ny_taxi` -> `Schemas` -> `public` -> `Tables`.
    *   Right-click on `yellow_tripdata` (or green) -> `View/Edit Data` -> `All Rows` to see the ingested data.

---

### Scheduling and Backfills

Now we will schedule the pipeline to run periodically using the flow `05_postgres_taxi_scheduled.yaml`, eliminating the need for manual execution.

This involves two key concepts:
*   **Scheduling**: Configuring the flow to automatically run at a set interval (e.g., monthly to download new data).
*   **Backfilling**: Running that same scheduled flow for a *past* date range to process historical data.

### Trigger (Schedule)
We can automate the workflow using a **Time-based Trigger**.
In the YAML file, we add a `triggers` section:
```yaml

triggers:
  - id: green_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    inputs:
      taxi: green

  - id: yellow_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 10 1 * *"
    inputs:
      taxi: yellow
```

This specific cron expression (`0 9 1 * *`) means: "Run at **09:00 AM** on the **1st day** of every month". We have a similar trigger for the yellow, but with time set at 10:00 so they won't overlap.

### Backfilling
Since we have historical data (e.g., from 2019 and 2020), simply scheduling it for *the future* isn't enough. We use Kestra's **Backfill** feature to process past data. We can do this directly from the UI. It is important that the date range that we set up includes the day and time in which the trigger would have been executed. For example, if we set up the end date as 2019-02-01 00:00:00, it won't include the 2019-02-01 execution (because the script has it scheduled to take place at 9 am).

---

## 4. ETL vs ELT (Google Cloud & BigQuery)

We have seen so far ETL pipelines.
There is a variation called **ELT** (Extract, Load, Transform), in which we load the data to the final destination, and then transform on top of that. It is convenient if we work in the cloud. We load it to the cloud and use the power that it provides us to transform it, using for example BigQuery.

Briefly the steps are:
1.  **Download the data** (through HTTP request, as we have done previously).
2.  **Load to Google Cloud Storage (GCS)**: We upload the files to a Bucket, which we will use as our Data Lake.
3.  **Transform in BigQuery**: Then we use the Data Warehouse (**BigQuery** in our case) to map to the data lake and add some metadata and perform other transformations.

**Two ways it is faster:**
1.  **Usage of the Cloud**: Leveraging the massive distributed computing power of the cloud.
2.  **No Full Load (External Tables)**: We are not loading all the data physically into BigQuery storage, but only referencing it from the Data Lake. So the original data stays untouched and we just run queries on top of it.

In this section we will modify the previous flow to an ELT pipeline which includes Google Cloud and BigQuery. 

### Setting up Google Cloud and BigQuery

To connect Kestra to your GCP account, follow these three steps:

#### 1. GCP credentials and variables configuration
To enable Kestra to interact with GCP we added the JSON key to KV store.

With the `06_gcp_kv` flow we crate the necessary variables within Kestra's KV store for subsequent flows.


#### 3. Create GCP Resources (`07_gcp_setup`)
Once the configuration is set, run this flow to provision the actual resources in Google Cloud.
1.  Execute `07_gcp_setup`.
2.  Kestra will:
    *   Create the GCS Bucket (if it doesn't exist).
    *   Create the BigQuery Dataset (if it doesn't exist).

I ran into a **403 Forbidden** error because my Service Account lacked the necessary permissions to create resources. To fix this, I assigned the **Storage Admin** and **BigQuery Admin** roles to my Service Account in the Google Cloud Console.

I checked that a new bucket and Bigquery are created in my google account and they are empty, so we are ready for next step. 

### Load data into BigQuery with ELT
This workflow (`08_gcp_elt_taxi.yaml`) is very similar to the `02_postgres_taxi.yaml` but instead of loading the data into Postgres, we load it into BigQuery. We will implemente scheduling and backfilling as well. 

Inputs stay the same, but the differences start at the level of variables, because we are not creating postgress tables. Instead we are referring to the file that we upload to our data lake. 



