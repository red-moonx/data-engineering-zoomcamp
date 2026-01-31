# Module 2 – Data Orchestration

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

## 2. Setting up Kestra (In Progress)

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
