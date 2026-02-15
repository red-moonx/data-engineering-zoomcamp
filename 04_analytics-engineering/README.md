# Module 4: Analytics Engineering

This module covers the Analytics Engineering part of the Data Engineering Zoomcamp.

## Introduction

**Data engineering** is the foundational practice of building and maintaining the infrastructure that moves raw data from disparate sources into a central warehouse, focusing on system architecture, scalability, and programming. **Analytics engineering**, a term coined in 2019 to describe tasks formerly handled by data engineers—takes over once that data has landed, applying software engineering best practices like version control, testing, and modularity to the transformation process. While the data engineer ensures data is available and moving, the analytics engineer ensures it is clean, reliable, and ready for business analysis; though these roles are now often separated in larger organizations, they remain deeply interconnected.

## dbt Fundamentals 
dbt (data build tool) is a transformation framework that allows data teams to model, test, and document data using SQL. It functions as the orchestrator for the Analytics Engineering phase, enabling developers to apply software engineering best practices, such as version control, testing, and modularity, to the data transformation process. Essentially, it converts raw data already in the warehouse into clean, reliable, and ready-to-use datasets.

### 1. ELT and dbt role
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

### 1. dbt and the ADLC
The Analytics Development Lifecycle (ADLC) takes different steps divided into two big areas: working directly with the data (plan, develop, test and deploy into production) and once the code is live, we have operations (operate, observe, discover and analyze).

dbt acts as **data control plane** in all steps of analytics: design, discover, align (consistent metrics) build, deploy and observe. 
