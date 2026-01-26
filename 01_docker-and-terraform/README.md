# Module 1: Containerization and Infrastructure as Code

This section contains my notes on the first module, covering the fundamentals of containerization with Docker and managing infrastructure as code. I made more emphasis on the concepts and the technical details that were more difficult for me to understand.

## 🏗️ Chapter 1: Environment Architecture & Dependency Management

### 1.1 Python Runtime Isolation
We utilize **GitHub Codespaces** as the host virtual machine. To manage project dependencies and the Python runtime, we use `uv` to create and maintain a **Virtual Environment** (`.venv`).
- **Technical Requirement**: Using a `.venv` within the Codespace ensures that the project's dependencies (Pandas, SQLAlchemy, Click) are isolated from the system's global Python interpreter.
- **Reproducibility**: This isolation guarantees that the `uv.lock` file captures exact versioning, which is critical for building a consistent Docker image later.

### 1.2 Docker Fundamentals
- **Docker Image**: A read-only, multi-layered file that includes the operating system, libraries, and application code.
- **Docker Container**: A runtime instance of an image. It utilizes the host's kernel but runs in an isolated user space.

### 1.3 The Dockerfile Template
The `Dockerfile` is a configuration script that automates the creation of a custom Docker Image. Below is the technical template used to containerize the ingestion pipeline:

```dockerfile
# 1. Specify the Base Image: Provides the OS (Debian/Alpine) and Python runtime
FROM python:3.12

# 2. Install Package Manager: Installing 'uv' for high-performance dependency resolution
RUN pip install uv

# 3. Set Working Directory: Defines the context for all subsequent COPY and RUN commands
WORKDIR /app

# 4. Dependency Layering: Copy only dependency definitions first
# This allows Docker to cache the 'uv sync' layer if these files haven't changed
COPY pyproject.toml uv.lock ./

# 5. Install Dependencies: Syncs the virtual environment inside the image
# The '--frozen' flag ensures versions match the lockfile exactly
RUN uv sync --frozen

# 6. Copy Application Logic: Transfer the ingestion script into the image
COPY ingest_data.py .

# 7. Define Entrypoint: Sets the executable that runs when the container starts
# It allows the container to function as an executable script
ENTRYPOINT ["uv", "run", "python", "ingest_data.py"]
```

---

## 🗄️ Chapter 2: Database Infrastructure (PostgreSQL)

### 2.1 Containerized Deployment
The PostgreSQL instance is deployed using a standard Docker container to provide a relational database management system (RDBMS).

```bash
docker run -it --rm \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:17
```

### 2.2 Network and Storage Configuration
- **Port Forwarding (`-p 5432:5432`)**: Maps the host machine's port 5432 to the container's port 5432. This allows external clients (the ingestion script running on the host) to communicate with the database engine via `localhost`.
- **Data Persistence (`-v`)**: Mounts a **Named Volume**. This ensures that the PostgreSQL data directory (`/var/lib/postgresql/data`) is persisted on the host's storage. If the container process is terminated, the data remains intact.

---

## ⚡ Data Ingestion Pipeline

### 2.3 Script Generation
The logic is initially developed in a **Jupyter Notebook** for iterative testing and is then exported to a standalone Python script for production execution:

```bash
uv run jupyter nbconvert --to=script notebook.ipynb
mv notebook.py ingest_data.py
```

### 2.4 Technical Implementation (`ingest_data.py`)
The ingestion script handles the data transfer between source files (Parquet/CSV) and the PostgreSQL destination:
1. **SQLAlchemy Engine**: Establishes a connection pool using the connection string: `postgresql://root:root@localhost:5432/ny_taxi`.
2. **Memory Management (Chunking)**: Uses the `chunksize` parameter (100,000 rows) to stream data. This prevents the Python process from exceeding the host's available RAM.
3. **Data Typing (Schema Enforcement)**: Explicitly defines the schema using `dtype` dictionaries to ensure correct database column types based on the requirements in `06-ingestion-script.md` (e.g., `Int64` for identifiers and `float64` for financial values).
4. **Parametrization (`click`)**: Implements a CLI interface to allow dynamic configuration of database credentials and target destinations without modifying the source code. Essentially, Click acts as a bridge between the Terminal and the Python script, allowing users to pass arguments to the script. We have implemented CLI with help of copilot

See ingest_data.py for the entire script. This file is then dockerized and included in the Dockerfile with the following line:

```dockerfile
COPY ingest_data.py .
```

## 🛠️ Verification and Interaction
- **pgcli**: A command-line interface for PostgreSQL with auto-completion and syntax highlighting. Used to verify the successful insertion of records.
  - *Connection*: `pgcli -h localhost -p 5432 -u root -d ny_taxi`
- **uv add --dev**: Adds development-only dependencies (like `pgcli` or `jupyter`) that are not included in the final production container, optimizing the image size.

## 💡 Summary of Key Technical Lessons
1. **Layer Caching**: Order matters in a Dockerfile; placing dependencies before source code minimizes build times.
2. **Network Bridges**: `localhost` in a client tool only works if the Docker container has explicitly published its ports to the host.
3. **Persistence**: Containers are ephemeral by design; volumes are the only way to ensure database state is preserved across restarts.

---

## 🗄️ Database Management: Moving from pgcli to pgAdmin
In the development phase, we used `pgcli` as a lightweight, terminal-based interface. However, for complex production-level database management, we transition to **pgAdmin4**.

### 1. Why pgAdmin? (Technical Benefits)
While `pgcli` is efficient for quick SQL execution, pgAdmin offers a comprehensive Graphical User Interface (GUI) that provides:
- **Visual Schema Navigation**: A browser tree to inspect tables, constraints, indexes, and triggers without writing `DESCRIBE` commands.
- **Query Tooling**: An advanced SQL editor with syntax highlighting, execution plan visualization, and data export features.
- **Monitoring**: Real-time dashboards to track database locks, active sessions, and hardware resource usage.

### 2. New Requirements: Docker Networking
Unlike the ingestion script (which runs on the host), pgAdmin runs as a separate containerized service. This introduces a new networking requirement: **Container-to-Container Communication**.

- **Isolation Problem**: By default, Docker containers are network-isolated. pgAdmin cannot "see" the postgres container even if both are running.
- **The Virtual Bridge**: We must create a Docker Network (e.g., `pg-network`) to act as a virtual switch.
- **DNS Resolution**: Inside a shared Docker network, containers resolve each other by their `--name` instead of an IP address.
- **Example**: Inside pgAdmin, the database hostname is no longer `localhost`; it is the container name, such as `pgdatabase`.

### 3. Summary of Configuration
- **External Access**: You access the pgAdmin interface via a web browser at `http://localhost:8085` (using the host's port mapping).
- **Internal Access**: pgAdmin connects to the database via the internal network bridge on port 5432.
- **Persistence**: A dedicated volume (`pgadmin_data`) is required to store server connection configurations and user settings.
