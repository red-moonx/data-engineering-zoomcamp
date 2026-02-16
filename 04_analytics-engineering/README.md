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