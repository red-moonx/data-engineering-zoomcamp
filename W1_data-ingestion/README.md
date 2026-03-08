# 🧪 Workshop 1: Data Ingestion

This section contains my notes and work for the [Data Ingestion Workshop](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/workshops/dlt.md), which focuses on building reliable data ingestion pipelines to data warehouses (for example, Snowflake) using **dlt** (data load tool), enhanced with LLMs, the dlt dashboard, and dlt MCP.

---

## Introduction
dlt is a python open source library that faciliates the main logic that we apply building and applying pipelines: schema evolution, normalization and data loading but still allows for customization. 

Essentially, dlt is python code, that we can structure in three main parts:
1. **Source**: object which contains all the information of our interest. Dlt uses a config-driven approach for defining a source.
2. **Building the pipeline**: in DLT the pipeline is an object that facilitates the extraction, transformation and loading of the data. Defining it is very simple, we specify name of pipeline and destination.
3. **Running the pipeline**: once source and pipeline are defined, we just call `pipeline.run(source)`.

```python
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source(
    {
        "client": {
            "base_url": "https://jaffle-shop.dlthub.com/api/v1",
        },
        "resources": ["customers", "products", "stores"],
    }
)

pipeline = dlt.pipeline(
    pipeline_name="rest_api_example",
    destination="duckdb",
    dataset_name="rest_api_data",
)

pipeline.run(source)
```

---

## dlt Demo: the traditional way

The use case for the demos is going to be the Search API from Open Library. This API allows us to query information on certain books.

Some key features we need to account for when retrieving data from a source are:

- **Pagination**: APIs typically return results in fixed-size pages (e.g. 100 records per page). To get the full dataset, we need to iterate through all pages — usually by incrementing an `offset` or `page` parameter until there are no more results. dlt's `rest_api_source` handles this automatically via its `paginator` config.
- **Rate limits**: Most public APIs cap how many requests you can make per second/minute to prevent abuse. If you exceed the limit, the API returns a `429 Too Many Requests` error. dlt handles this by respecting `Retry-After` headers and backing off automatically.
- **Retries**: Network calls can fail transiently (timeouts, 5xx errors). A robust pipeline should automatically retry failed requests with exponential backoff rather than failing the entire run. dlt has built-in retry logic for this.

### What the response looks like for this API?

For the Open Library API, the response is structured as a nested JSON object where specific fields are designed to handle multiple related data points. For instance, the "author_name" and "author_key" fields are nested as arrays (using square brackets []) to allow for cases where a book has more than one creator, even if only one is listed. This format will need to be restructed ccording to the destination of our choice, like a relational database. 
Essentially we need the content to be transformed so it is compatible with our destination.

The full implementation is in [`open_library_pipeline.py`](dlt/open_library_pipeline.py). Below we highlight the main parts.

**1. Defining the source**

dlt uses `rest_api_source` with a config-driven approach. The source config is broken into three key parts:

- **`client`** — sets the `base_url` common to all requests (`https://openlibrary.org`). For this example is not needed, but for APIs that require authentication, this will be included as well in "client".
- **`endpoint.params`** — the query parameters documented by the API: `q` (search term) and `limit` (number of results per page).
- **`paginator`** — tells dlt how to walk through pages automatically. Here we use `offset`-based pagination, pointing at the `numFound` field in the response to know when to stop.

Note: other parameters of this rest_api_source function are dlt-specific, and therefore dont change from one API to another.

```python
return rest_api_source({
    "client": {
        "base_url": "https://openlibrary.org",
    },
    "resources": [
        {
            "name": "books",
            "endpoint": {
                "path": "search.json",
                "params": {
                    "q": query,      # search term, e.g. "harry potter"
                    "limit": 100,    # results per page
                },
                "data_selector": "docs",   # the key in the JSON response that holds the records
                "paginator": {
                    "type": "offset",
                    "limit": 100,
                    "offset_param": "offset",
                    "limit_param": "limit",
                    "total_path": "numFound",  # total record count returned by the API
                },
            },
        },
    ],
})
```
Rate limits and retries are handled by default (when we use the `rest_api_source` function)


**2. Defining the pipeline**
Then we define the pipeline. In this case, the pipeline is going to send the data that we are collecting in our source, to duckdb. Duckdb database will be generated when running the code (is therefore very demo friendly). but we can of course, send it to another databsase like "BigQuery", also providing the credentials. 

**3. Running the pipeline: pipeline.run()**
This one liner runs three different functions behind the curtain, resembling the ETL logic:
- *Extract*: we get a table (named books)
- *Normalize*: here dlt transforms raw JSON into a relational structure. Besides adding new columns and fields, dlt also generates its own metadata.
- *Load* the data into the destination. 

At this point we have the data in the database, but we are on our own if we want to inspect the data, or query it.

Unless we implement a workflow to leverage better LLM tools for writing pipelines, etc. 


## The AI-assisted way: dltHub workspace workflow
1. Step 1: Load data (LLM scaffolds). These are templates that dlt has created that give step by step instructions to create a project and writing prompts tu create and run the dlt project. Basically, this will give instructions tailored to our source, with minimal debugging. 

2. Ensure quality: inspection and validation, basic checks, etc. For example, dlt dashboard and dlt MCP server. 

3. Create reports and transformations. Dlt proposes the combination of two tools: marimo (reactive notebooks; avoid outdated stale outputs) and the IBIS library (python library that creates an abstraction layer that helps us interact with our database of choice; database agnostic tool).

### MCP server configuration

In the workshop, Cursor is the recommended IDE. Here, we're replicating the same setup using **Antigravity**. The steps were:

1. **Locate Antigravity's MCP config file** — found at `~/.gemini/antigravity/mcp_config.json` (empty by default).

2. **Write the dlt MCP server config** — same JSON as the Cursor config from the workshop, using `uv` to run `dlt-mcp`:

```json
{
  "mcpServers": {
    "dlt": {
      "command": "uv",
      "args": [
        "run",
        "--with", "dlt[duckdb]",
        "--with", "dlt-mcp[search]",
        "python", "-m", "dlt_mcp"
      ]
    }
  }
}
```

3. **Verify the package works** — confirmed `dlt-mcp` installs and loads correctly via `uv`.

4. **Restart the Antigravity session** — the config takes effect on next session start, giving the AI access to dlt tools (list pipelines, inspect schemas, query tables, etc.).


## dlt Demo (AI-assisted)

### Step 1: Create a New Project Folder

Create a dedicated folder for the AI-assisted pipeline, separate from the traditional demo:

```bash
mkdir dlt-ai-workshop
cd dlt-ai-workshop
```

### Step 2: Initialize a uv Project

Instead of using a global Python environment, we use `uv` to create an isolated, reproducible project:

```bash
uv init
```

This generates:
- `pyproject.toml` — project metadata and dependency list
- `.python-version` — pins the Python version
- `.venv/` — virtual environment (created automatically on first `uv add`)

### Step 3: Install dlt with Workspace Extras

```bash
uv add "dlt[workspace]==1.22.2"
```

The `[workspace]` extra installs the `dlt init` CLI scaffolding tool, along with all core dlt dependencies (DuckDB, marimo, ibis-framework, etc.). *Note: We pin to `1.22.2` to match the exact behavior of the workshop video, as `1.23.0` introduced significant CLI changes.* `uv` manages the `.venv` automatically — no manual activation needed.

> **Why `uv` instead of plain `pip`?**  
> `uv` creates a project-level virtual environment (`.venv/`) so dependencies are fully isolated. It's also significantly faster than `pip` and keeps a `pyproject.toml` as a reproducible record of dependencies.

### Step 4: Scaffold the dlt Workspace

```bash
uv run dlt init dlthub:open_library duckdb
```

This scaffolds a generic REST API pipeline template. The files created are:

| File | Purpose |
|------|---------|
| `open_library_pipeline.py` | Main pipeline file — source, pipeline config, and runner |
| `.dlt/` | Local dlt config folder (credentials, settings) |
| `.gitignore` | Pre-configured to exclude secrets and `.venv` |

#### What's inside `open_library_pipeline.py`?

The scaffolded file follows the same 3-step pattern we already know (source → pipeline → run), but the **configuration is not filled in yet** — it only contains placeholders:

```python
config: RESTAPIConfig = {
    "client": {
        # TODO set base URL for the REST API
        "base_url": "https://example.com/v1/",
        # TODO configure the right authentication method or remove
        "auth": {"type": "bearer", "token": access_token},
    },
    "resources": [
        # TODO define resources per endpoint
    ],
}
```

This is intentional — **the LLM agent is responsible for filling in the correct configuration** (base URL, endpoints, pagination, auth, etc.) based on the Open Library API spec. This is the core of the AI-assisted workflow.

> **Note:** `dlt` prints a deprecation warning suggesting `dlt ai init` instead of `dlthub:<source>`. The new command `uv run dlt ai init` starts an interactive AI-guided workflow. Both approaches work; the workshop uses the `dlthub:` syntax for compatibility.

### Step 5: Install dlt AI Rules for the Agent

When using Cursor, `dlt init` automatically generates `.cursor/rules/*.mdc` files. Since we are using Antigravity (a Gemini-based agent), we can explicitly generate the equivalent rules and skills for our agent using the dlt AI toolkit:

```bash
uv run dlt ai toolkit rest-api-pipeline install --agent claude
mv .claude .gemini
```

*(Note: We use the `claude` template because dlt doesn't have a native `gemini` one yet, but the markdown rules are agent-agnostic so we just rename the folder).*

This creates a `.gemini/` directory containing two key folders:
- `rules/`: Contains the workflow instructions (e.g., `rest-api-pipeline-workflow.md`, `init-dlthub-workspace.md`) detailing best practices for writing dlt pipelines.
- `skills/`: Contains specific task guidelines (e.g., `find-source`, `create-rest-api-pipeline`, `validate-data`, `setup-secrets`).

**How to use them:** While Cursor automatically injects its `.mdc` rules, for Antigravity, we can explicitly ask the agent to `"read the .gemini rules and skills before writing the pipeline"` to ensure it follows dlt's official, battle-tested guidelines. The dlt MCP server provides complimentary access to the docs on-demand.

---


### Step 6: running the prompt to fill in the pipeline
The next step is to actually write the prompt that instructs the AI (Antigravity) to:
- Read the `.gemini` rules to understand best practices
- Read the `open_library-docs.yaml` to understand the API parameters and pagination
- Fill in the placeholders in `open_library_pipeline.py` to create a working REST API pipeline.

```text
Please generate a REST API Source for Open Library API, as specified in `open_library-docs.yaml`
use the search api and query harry potter books
Place the code in open_library_pipeline.py and name the pipeline open_library_pipeline.
If the file exists, use it as a starting point.
Do not add or modify any other files.
Use `.gemini` rules as a tutorial.
After adding the endpoints, allow the user to run the pipeline with python open_library_pipeline.py and await further instructions.
```

#### Pipeline Configuration Summary
Based on the provided specifications, the AI automatically configures the pipeline with:
- **Base URL**: `https://openlibrary.org`
- **Endpoint**: `/search.json`
- **Query Parameters**: `q="harry potter"` and `limit=100`
- **Data Selector**: `docs` (to extract the book array from the response object)
- **Pagination**: Offset-based pagination with `total_path="numFound"` to automatically iterate through all result pages.

#### Running the pipeline
I run the pipeline with the code
`uv run open_library_pipeline.py`

Sccessfully. 
Pipeline open_library_pipeline load step completed in 1.39 seconds
1 load package(s) were loaded to destination duckdb and into dataset open_library_pipeline_dataset
The duckdb destination used duckdb:////workspaces/data-engineering-zoomcamp/W1_data-ingestion/dlt-ai-workshop/open_library_pipeline.duckdb location to store data
Load package 1772977180.2625802 is LOADED and contains no failed jobs


### Step 7: Dashboard
uv run dlt pipeline open_library_pipeline show

It offers a comprenhensive visualization of everything
We can directly query using the MCP tool. 

