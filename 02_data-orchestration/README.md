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

### Key Orchestration Takeaway: Data Passing
We never manually pass the raw data between tasks. Instead, we pass **references (URIs)**. Kestra handles the heavy lifting of ensuring that the file produced by one task is available in the working directory of the next, even if they run in different containers or environments.

---
