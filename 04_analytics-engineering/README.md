# Module 4: Analytics Engineering

This module covers the Analytics Engineering part of the Data Engineering Zoomcamp.

## Introduction

**Data engineering** is the foundational practice of building and maintaining the infrastructure that moves raw data from disparate sources into a central warehouse, focusing on system architecture, scalability, and programming. **Analytics engineering**, a term coined in 2019 to describe tasks formerly handled by data engineers—takes over once that data has landed, applying software engineering best practices like version control, testing, and modularity to the transformation process. While the data engineer ensures data is available and moving, the analytics engineer ensures it is clean, reliable, and ready for business analysis; though these roles are now often separated in larger organizations, they remain deeply interconnected.

## Tooling Landscape
The modern analytics engineering stack follows a clear linear path:
**Data Loading** → **Data Storing** (Cloud Data Warehouses: Snowflake, BigQuery, Redshift) → **Data Modeling** (dbt, Dataform) → **Data Presentation** (BI tools: Looker, Tableau, Google Data Studio, Mode).

---

## Data Modeling Concepts

### ETL vs. ELT
* **ETL (Extract, Transform, Load):** Slightly more stable and compliant for specific data analysis needs, but often results in higher storage and compute costs.
* **ELT (Extract, Load, Transform):** Provides faster and more flexible analysis with lower maintenance costs. It leverages the massive compute power of modern cloud data warehouses to handle transformations after the data is stored.

#### The ELT Process and dbt
The ELT (Extract, Load, Transform) workflow is a modern data strategy where, in contrast with ETL, raw data is loaded into a warehouse before being transformed, utilizing the warehouse's own computational power. The benefits of ELT are:

**Leverages Cloud Power**: Uses the massive processing capabilities of platforms like BigQuery and Snowflake to handle transformations at scale.

**Faster Availability**: Raw data is accessible for analysis immediately since it doesn't have to wait for transformation before loading.

**Cost & Flexibility**: Reduces the need for expensive on-premises hardware and allows teams to transform data iteratively as business needs evolve.

**Data Democratization**: Provides a self-service model where analysts can access and transform data without being bottlenecked by upstream processes.

dbt serves as the transformation layer within the warehouse during the ELT process. It provides the tools to manage and automate the "T" (Transform) step through several key features:
- Version Control: Tracks all transformation changes to ensure consistency and team collaboration.
- Automation: Schedules transformation processes so that analysis is always performed on the most up-to-date data.
- Testing: Includes built-in validation to ensure data quality and integrity throughout the workflow.

### Kimball’s Dimensional Modeling
Kimball’s Dimensional Modeling is a data warehousing design approach focused on making data easy for business users to understand and fast for systems to query. 

* **Fact Tables:** Contain quantitative metrics or measurements, such as sale amounts or transaction counts.
* **Dimension Tables:** Provide the descriptive context (the "who, what, where") like product names, customer details, or dates.
* **Star Schema:** This "bottom-up" method typically results in a central fact table surrounded by dimensions. 
* **The Grain:** In a modern ELT workflow using **dbt and BigQuery**, this modeling is essential for defining the "grain"—the specific level of detail for each row—to ensure the resulting datasets are accurate and analytics-ready.

### Architecture of Dimensional Modeling
1. **Stage Area:** Contains raw data. This is a landing zone usually accessible only to Data Engineers and Analytics Engineers to ensure data integrity.
2. **Processing Area:** The transformation layer where data moves from raw to structured models. It focuses on computational efficiency and enforcing organizational standards.
3. **Presentation Area:** The final layer where cleaned, modeled data is exposed to BI tools and business users for reporting.

---

## dbt Fundamentals
**dbt (data build tool)** is a transformation framework that allows teams to deploy analytics code using SQL while following software engineering best practices like **modularity, portability, CI/CD, and documentation**. It functions as the orchestrator for the Analytics Engineering phase, enabling developers to apply software engineering best practices, such as version control, testing, and modularity, to the data transformation process. Essentially, it converts raw data already in the warehouse into clean, reliable, and ready-to-use datasets.

In a typical dbt workflow, development happens in a **sandbox** environment. This allows for separate environments for testing and documentation before final deployment to production via CI/CD pipelines.

### How does it work?
dbt simplifies the development process by handling the "boilerplate" code for you:
* **The `.sql` File:** Each model is saved as a simple `.sql` file.
* **The SELECT Statement:** You only write the `SELECT` logic. You do **not** need to write **DDL** (Data Definition Language like `CREATE TABLE`) or **DML** (Data Manipulation Language like `INSERT INTO`).
* **The Compiler:** dbt takes your SELECT statement, wraps it in the necessary DDL/DML for your specific warehouse (e.g., BigQuery), and executes it to create the final table or view.

#### Example: dbt in Action
**What you write in your dbt model (`total_spend.sql`):**
```sql
select 
    user_id, 
    sum(order_amount) as total_spent
from raw_orders
group by 1
```
What dbt "compiles" and runs in BigQuery behind the scenes:

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
The Analytics Development Lifecycle (ADLC) takes different steps divided into two big areas: working directly with the data (plan, develop, test and deploy into production) and once the code is live, we have operations (operate, observe, discover and analyze).

dbt acts as **data control plane** in all steps of analytics: design, discover, align (consistent metrics) build, deploy and observe. 

---

## How to use dbt?
There are two primary ways to work with dbt: **dbt Core** and **dbt Cloud**.

### dbt Core (Open-Source)
This is the open-source project that handles the actual data transformation logic.
* **Functionality:** It builds and runs dbt projects consisting of `.sql` and `.yml` files.
* **Technical Layers:** It includes the SQL compilation logic, macros, and database adapters needed to talk to your warehouse.
* **Interface:** It uses a Command Line Interface (CLI) to run dbt commands locally.
* **Cost:** It is open-source and free to use.

#### 1. dbt Core (The Engine)
This is the free, open-source version that you install on your own computer or server.

How you use it: You work in your own code editor (like VS Code) and type commands into a terminal.

Your Responsibility: You have to set up everything yourself: the connection to BigQuery, the scheduling (e.g., using GitHub Actions or Airflow), and hosting the documentation website.

Best for: Developers who want full control and don't want to pay a subscription fee.

### dbt Cloud (SaaS)
This is a managed platform (Software as a Service) designed to simplify the development and management of dbt projects.
* **Development Environment:** Provides a web-based IDE and a cloud-native CLI to develop, run, and test projects.
* **Operations:** Includes managed environments, job orchestration, logging, and alerting.
* **Advanced Features:** Offers integrated documentation, an Admin and metadata API, and the dbt Semantic Layer.

#### 2. dbt Cloud (The Managed Platform)
This is a paid "all-in-one" platform that runs in your web browser.

How you use it: You log into a website. It has a built-in code editor, buttons to run your code, and it handles your Git connections for you.

What’s included: It has a built-in Scheduler (no need for extra tools), automatically hosts your documentation, and provides a visual map (DAG) of your data. 

Best for: Teams that want to skip the "it works on my machine" headache and start modeling immediately without managing infrastructure. No need to worrie about documentation, orchestration, environment set up, back up etc. It also come with collaboration features. 


### Workshop Implementation
Depending on the database, the setup changes:

* **BigQuery (Cloud Setup):**
    - Developed using the **dbt Cloud IDE**.
    - **No local installation** of dbt Core is required.
    - High-level workflow: `BigQuery (Data) <-> dbt Cloud (IDE)`.

* **Postgres (Local Setup):**
    - Developed using a **Local IDE** (e.g., VS Code).
    - Requires a **Local installation** of dbt Core via CLI.
    - Uses a `profiles.yml` file to manage database credentials.

### Project Implementation Options
This workshop offers two distinct paths depending on your learning objectives: the Enterprise Track and the Developer Track. The dbt Cloud + BigQuery option aims to simulate a professional, cloud-native production environment, focusing on team collaboration and managed infrastructure. Alternatively, the dbt Core + DuckDB option is designed for a lightweight, local developer experience, offering a completely free and fast setup that is ideal for rapid prototyping and offline development.

---

### The Next Generation: dbt Fusion
Released in 2025, **dbt Fusion** is the new high-performance engine written in **Rust**. It replaces the legacy Python engine to provide:
* **30x Faster Parsing:** Large projects compile in milliseconds.
* **Pre-run Validation:** Catches SQL errors before they hit the warehouse.
* **Smart Rebuilds:** Uses column-level awareness to skip unnecessary model runs and save costs.
* **Real-time IDE:** Powers the dbt VS Code extension with live lineage and previews.

dbt Core is still there but, definitely is being replaced by dbt fusion.  The issue with dbt fussion is that it is not adopted by every single adopter out there (like duckdb). 
