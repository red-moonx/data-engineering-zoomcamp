# Module 5: Data Platforms

These are my notes on Module 5 of the Data Engineering Zoomcamp, covering data platforms and end-to-end pipeline building with Bruin.

---

## Installation

### Bruin CLI

Install the Bruin CLI (works on GitHub Codespaces / Linux):

```bash
curl -LsSf https://getbruin.com/install/cli | sh
source ~/.bashrc
```

Verify the installation:

```bash
bruin version
# Current: v0.0.0-test (392f275c9064399fc263d2da3de811210c6dc76f)
```

### VS Code Extension

Install the **Bruin** extension from the VS Code marketplace. It adds a Bruin panel to the IDE for running assets and pipelines, viewing lineage, and rendering queries directly from the editor.

### Bruin MCP (AI Agent Integration)

MCP (Model Context Protocol) lets a VS Code AI agent communicate directly with Bruin — running commands, validating pipelines, querying data, and creating assets on your behalf.

> **Note:** Since I am using **Antigravity** as  AI assistant, we don't strictly need MCP — Antigravity already has direct access to the project and can run Bruin commands on its own. However, we set it up anyway in case we switch to another agent like GitHub Copilot or Cursor AI, which do require MCP to interact with Bruin.

To enable it, create `.vscode/mcp.json` at the root of the project:

```json
{
  "servers": {
    "bruin": {
      "command": "bruin",
      "args": ["mcp"]
    }
  }
}
```

Once configured, the AI agent in VS Code will have direct access to your Bruin project.

---

## Project Initialization

### Why Bruin needs Git

Bruin requires the project folder to be a git repository. It uses git to:

- Detect the root of the project
- Track changes to assets and pipelines
- Automatically add `.bruin.yml` to `.gitignore` to prevent credentials/secrets from being pushed to GitHub

Since the workspace is already a git repo, there's no need to initialize it separately — Bruin detects it automatically.

### Initializing a Bruin project

```bash
bruin init default bruin-pipeline
```

This creates a new project from the `default` template inside the `bruin-pipeline/` folder. The structure looks like:

```text
bruin-pipeline/
├── .bruin.yml        # Environment and connection config (gitignored — contains secrets)
├── pipeline.yml      # Pipeline name, schedule, default connections
└── assets/
    └── ...           # Asset files (SQL, Python, YAML)
```

> To validate the project structure right away:
> ```bash
> bruin validate bruin-pipeline
> ```
