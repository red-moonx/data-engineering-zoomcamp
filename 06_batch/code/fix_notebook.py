import json
import os

# Path to your notebook
notebook_path = '/workspaces/data-engineering-zoomcamp/06_batch/code/05_taxi_schema.ipynb'

if not os.path.exists(notebook_path):
    print(f"❌ Error: Could not find notebook at {notebook_path}")
    exit(1)

# Load the notebook
with open(notebook_path, 'r') as f:
    try:
        nb = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        exit(1)

# 1. Add Java Setup cell at the top
java_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "java-setup",
    "metadata": {},
    "outputs": [],
    "source": [
        "import os\n",
        "os.environ[\"JAVA_HOME\"] = \"/usr/local/sdkman/candidates/java/21.0.9-ms\"\n",
        "os.environ[\"PATH\"] = os.environ[\"JAVA_HOME\"] + \"/bin:\" + os.environ[\"PATH\"]"
    ]
}

# Check if we already added it so we don't double up
if nb['cells'][0].get('id') != "java-setup":
    nb['cells'].insert(0, java_cell)
    print("✅ Added Java setup cell.")

# 2. Fix 2021 loops (change range(1, 13) to range(1, 8))
updated_loops = 0
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source_list = cell['source']
        if isinstance(source_list, list):
            source_str = "".join(source_list)
        else:
            source_str = source_list
            
        if 'year = 2021' in source_str and 'range(1, 13)' in source_str:
            cell['source'] = [line.replace('range(1, 13)', 'range(1, 8)') for line in cell['source']]
            updated_loops += 1

print(f"✅ Updated {updated_loops} loops (Green and Yellow).")

# Save the updated notebook
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("🚀 Notebook is now ready to run!")
