#!/usr/bin/env python3

# This script serves as a preprocessing tool for mkdocs.
# It is designed to parse dataset instances from the ./dataset directory,
# and subsequently generate .md files within the docs/datasets directory.
# These .md files are then automatically rendered by mkdocs to create the site.

import csv
import os
import yaml

from jinja2 import Template
import requests

# Parse dataset instances from the ./datasets directory

# Each dataset instance is represented by a directory within the ./datasets directory
# With metadata stored in a metadata.yaml, schema ddl in schema.ddl.ngql
# There are different profiles of datasets(flavors): tiny, small, medium, large, huge etc.
# Each profile was already defined in the metadata.yaml file and the corresponding data files
# are stored in the directory with the same name as the profile. i.e. ./datasets/tiny

dataset_ids = os.listdir("./datasets")
dataset_map = {}

# Metadata Keys:
DATASET_NAME = "name"
DATASET_DESCRIPTION = "description"
DATASET_FLAVORS = "profiles"
DATASET_LICENSE = "license"
DATASET_TAGS = "tags"
DATASET_AUTHOR = "author"
DATASET_HUB_CONTRIBUTOR = "contributor"
DATASET_HOMEPAGE = "homepage"

## Asset Related Keys:
DATASET_VIDEO = "video"
DATASET_HTML_IFRAME = "iframe"
DATASET_SCREEN_CAPTURE = "screen_capture"
DATASET_GEPHI_LITE_FILE = "gephi_lite_file"
DATASET_JUPYTER_LOAD_LINES = "jupyter_nebulagraph_load_lines"
DATASET_NEBULA_IMPORTER_CONF = "nebula_importer"

# Schmea Related Keys:
DATASET_STRUCTURE_MERMAID = "structure_mermaid"
DATASET_PROPERTIES_MERMAID = "properties_mermaid"
DATASET_DDL = "ddl"


def parse_metadata(dataset_id):
    metadata = {}
    try:
        with open(f"./datasets/{dataset_id}/metadata.yaml") as f:
            metadata = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print(f"Error: metadata.yaml not found for dataset {dataset_id}")
    except yaml.YAMLError as e:
        print(f"Error: metadata.yaml is invalid for dataset {dataset_id}, {e}")
    # Format metadata
    # "" value is replaced with None
    for key, value in metadata.items():
        if value == "":
            metadata[key] = None
    # Validate metadata
    ## Name, Description, Profiles are required
    assert (
        metadata.get(DATASET_NAME) is not None
    ), f"Error: {DATASET_NAME} is required for dataset {dataset_id}"
    assert (
        metadata.get(DATASET_DESCRIPTION) is not None
    ), f"Error: {DATASET_DESCRIPTION} is required for dataset {dataset_id}"
    assert (
        metadata.get(DATASET_FLAVORS) is not None
    ), f"Error: {DATASET_FLAVORS} is required for dataset {dataset_id}"

    return metadata


def parse_schema(dataset_id):
    schema = ""
    try:
        with open(f"./datasets/{dataset_id}/schema.ddl.ngql") as f:
            schema = f.read()
    except FileNotFoundError:
        print(f"Error: schema.ddl.ngql not found for dataset {dataset_id}")
    return schema


# Parse metadata and schema for each dataset instance
for dataset_id in dataset_ids:
    metadata = parse_metadata(dataset_id)
    schema = parse_schema(dataset_id)
    dataset_map[dataset_id] = {
        DATASET_DDL: schema,
        DATASET_NAME: metadata.get(DATASET_NAME),
        DATASET_DESCRIPTION: metadata.get(DATASET_DESCRIPTION),
        DATASET_FLAVORS: metadata.get(DATASET_FLAVORS),
        DATASET_VIDEO: metadata.get(DATASET_VIDEO),
        DATASET_HTML_IFRAME: metadata.get(DATASET_HTML_IFRAME),
        DATASET_SCREEN_CAPTURE: metadata.get(DATASET_SCREEN_CAPTURE),
        DATASET_GEPHI_LITE_FILE: metadata.get(DATASET_GEPHI_LITE_FILE),
        DATASET_STRUCTURE_MERMAID: metadata.get(DATASET_STRUCTURE_MERMAID),
        DATASET_PROPERTIES_MERMAID: metadata.get(DATASET_PROPERTIES_MERMAID),
        DATASET_LICENSE: metadata.get(DATASET_LICENSE),
        DATASET_TAGS: metadata.get(DATASET_TAGS),
        DATASET_AUTHOR: metadata.get(DATASET_AUTHOR),
        DATASET_HUB_CONTRIBUTOR: metadata.get(DATASET_HUB_CONTRIBUTOR),
        DATASET_HOMEPAGE: metadata.get(DATASET_HOMEPAGE),
        DATASET_JUPYTER_LOAD_LINES: metadata.get(DATASET_JUPYTER_LOAD_LINES),
        DATASET_NEBULA_IMPORTER_CONF: metadata.get(DATASET_NEBULA_IMPORTER_CONF),
    }

# Sample CSV files from first profile of each dataset instance
# These sampled dataframes are used to render tables in the dataset instance pages

# DataSample Keys:
DATASET_SAMPLE_DATA = "sample_data"

for dataset_id in dataset_ids:
    profile = dataset_map[dataset_id][DATASET_FLAVORS][0]
    sample_data = {}
    try:
        profile_path = f"./datasets/{dataset_id}/{profile}"
        if os.environ.get("WITH_GITLFS") == "true":
            for file in os.listdir(profile_path):
                if file.endswith(".csv"):
                    table_name = file[:-4]  # Remove .csv extension
                    with open(os.path.join(profile_path, file), "r") as csvfile:
                        reader = csv.reader(csvfile)
                        rows = list(reader)[:5]  # Sample up to 5 rows
                        sample_data[table_name] = rows
                        # escape "|" in the csv file
                        sample_data[table_name] = [
                            [cell.replace("|", ",") for cell in row] for row in rows
                        ]
        else:
            for file in os.listdir(profile_path):
                if file.endswith(".csv"):
                    table_name = file[:-4]  # Remove .csv extension
                    response = requests.get(
                        f"https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/{dataset_id}/{profile}/{file}"
                    )
                    if response.status_code == 200:
                        content = response.content.decode("utf-8")
                        csv_reader = csv.reader(content.splitlines())
                        rows = list(csv_reader)[:5]  # Sample up to 5 rows
                        sample_data[table_name] = rows
                        # escape "|" in the csv file
                        sample_data[table_name] = [
                            [cell.replace("|", ",") for cell in row] for row in rows
                        ]
    except Exception as e:
        print(f"Error sampling data for dataset {dataset_id}: {e}")
    dataset_map[dataset_id][DATASET_SAMPLE_DATA] = sample_data

# Generate .md files for each dataset instance

DEMO_CONTENT_TAB_FILEDS = [
    DATASET_VIDEO,
    DATASET_HTML_IFRAME,
    DATASET_SCREEN_CAPTURE,
]

SCHEMA_CONTENT_TAB_FILEDS = [
    DATASET_STRUCTURE_MERMAID,
    DATASET_PROPERTIES_MERMAID,
    DATASET_DDL,
]

dataset_showcase_template_j2 = """
# {{ dataset["name"] }}

{% if dataset["author"] %} ![Author](https://img.shields.io/badge/Author-{{ dataset["author"]["name"] | replace(" ", "%20") }}-blue) {% endif %}
{% if dataset["license"] %} [![License](https://img.shields.io/badge/License-{{ dataset["license"] | replace(" ", "%20") | replace("-", "%20") }}-blue.svg)](https://opensource.org/licenses/{{ dataset["license"] }}) {% endif %}
{% if dataset["homepage"] %} [![Homepage](https://img.shields.io/badge/Home-Page-blue.svg)]({{ dataset["homepage"] }}) {% endif %}
{% if dataset["contributor"] %} ![Contributor](https://img.shields.io/badge/AddedBy-{{ dataset["contributor"]["name"] | replace(" ", "%20") }}-blue) {% endif %}

{% if dataset["tags"] %}
**Tags:** {% for tag in dataset["tags"] %}`{{ tag }}`{% if not loop.last %}, {% endif %}{% endfor %}
{% endif %}


> {{ dataset["description"] }} [Download :fontawesome-solid-download:](#download){ .md-button }


## Data Showcase

{% if dataset["video"] %}
=== "Demo Video"
    <iframe width="100%" height="420" src="{{ dataset["video"] }}" frameborder="0" allowfullscreen></iframe>
{% endif %}

{% if dataset["iframe"] %}
=== "Graph Visualization"
    <iframe src="{{ dataset["iframe"] }}" width="100%" height="420"></iframe>
{% endif %}

{% if dataset["screen_capture"] %}
=== "Screen Capture"
    ![Screen Capture]({{ dataset["screen_capture"] }})
{% endif %}
## Schema

=== "DDL nGQL"
    ```sql
    {{ dataset["ddl"] | indent(4) }}
    ```
    [Download DDL](https://github.com/wey-gu/awesome-graph-dataset/tree/main/datasets/{{ dataset_id }}/schema.ddl.ngql){ .md-button }

{% if dataset["structure_mermaid"] %}
=== "Structure"
    <div style="text-align: center;">

    ```mermaid
    {{ dataset["structure_mermaid"] | indent(4) }}
    ```

    </div>
{% endif %}

{% if dataset["properties_mermaid"] %}
=== "Properties"
    <div style="text-align: center;">
    
    ```mermaid
    {{ dataset["properties_mermaid"] | indent(4) }}
    ```

    </div>
{% endif %}

## Sample Data

{% for table_name, rows in dataset["sample_data"].items() %}
=== "{{ table_name }}"
    | {% for column in rows[0] %}{{ column }} |{% endfor %}{% set column_count = rows[0] | length %}
    | {% for _ in range(column_count) %}:---:|{% endfor %}{% for row in rows[1:] %}
    | {% for cell in row %}{{ cell }} |{% endfor %}{% endfor %}
{% endfor %}

## Download

=== "Files"
    
    [Browse Files](https://github.com/wey-gu/awesome-graph-dataset/tree/main/datasets/{{ dataset_id }}){ .md-button }

{% if dataset["gephi_lite_file"] %}
=== "Gephi Lite File"
    
    [Download Gephi Lite File](https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/{{ dataset_id }}/{{ dataset["gephi_lite_file"] }}){ .md-button }

{% endif %}

{% if dataset["jupyter_nebulagraph_load_lines"] %}
=== "Jupyter-NebulaGraph"

    Install the Jupyter-NebulaGraph extension, refer to the [documentation](https://jupyter-nebulagraph.readthedocs.io/) for more information.

    ```python
    !pip install jupyter-nebulagraph
    %load_ext ngql
    %ngql --address 127.0.0.1 --port 9669 --user root --password nebula
    ```
    
    Create Graph Space and Schema.
    
    ```python
    %ngql CREATE SPACE {{ dataset_id }}(partition_num=1, replica_factor=1, vid_type=fixed_string(128));
    # wait for a while
    %ngql USE {{ dataset_id }};
    ```
    
    ```sql
    # DDL with `%%ngql` magic for multi-line execution
    %%ngql
    {{ dataset["ddl"] | indent(4) }}
    ```
    
    > Refer to [jupyter-nebulagraph](https://jupyter-nebulagraph.readthedocs.io) for more information.
    
    ```python
    {{ dataset["jupyter_nebulagraph_load_lines"] | indent(4) }}
    ```
    
    {% endif %}

{% if dataset["nebula_importer"] %}
=== "Nebula Importer"

    The [Nebula Importer](https://github.com/vesoft-inc/nebula-importer) is a tool for importing data from various data sources into NebulaGraph.

    We provide a [configuration file]({{ dataset["nebula_importer"].get("conf_file", "#") }}) for the Nebula Importer(version: {{ dataset["nebula_importer"].get("version", "v4") }}) to import the dataset.

    Reference call command, assuming the configuration file is named `{{ dataset["nebula_importer"].get("conf_file_name", "importer_v4_config.yaml") }}` in your current directory:

    ```shell
    # get the configuration file
    # modify the configuration file according to your environment

    # ls -l ./data/{{ dataset_id }}/{{ profile }}
    
    # ls -l {{ dataset["nebula_importer"].get("conf_file_name", "importer_v4_config.yaml") }}
    
    # run the importer
    docker run --rm -ti \\
        -v ${PWD}/data/{{ dataset_id }}/{{ profile }}:/data \\
        -v ${PWD}/{{ dataset["nebula_importer"].get("conf_file_name", "importer_v4_config.yaml") }}:/root/importer_{{ dataset["nebula_importer"].get("version", "v4") }}_config.yaml \\
        vesoft/nebula-importer:{{ dataset["nebula_importer"].get("version", "v4") }} \\
        -c /root/importer_{{ dataset["nebula_importer"].get("version", "v4") }}_config.yaml
    ```
{% endif %}
"""

dataset_index_template_j2 = """
# Datasets

| Dataset Name | Tags | Sizes | Description |
| ------------ | ---- | ----- | ----------- | {% for dataset_id in dataset_ids %}
| [{{ dataset_map[dataset_id].get("name", "N/A") }}](./{{ dataset_id }}) | {% for tag in dataset_map[dataset_id].get("tags", ["N/A"]) %}`{{ tag }}`{% if not loop.last %}, {% endif %}{% endfor %} | {% for size in dataset_map[dataset_id].get("profiles", ["N/A"]) %}`{{ size }}`{% if not loop.last %}, {% endif %}{% endfor %} | {{ dataset_map[dataset_id].get("description", "N/A").replace("\n", "<br>") }} | {% endfor %}
"""

## TODOS
# - render download files URLs

for dataset_id in dataset_ids:
    with open(f"./docs/datasets/{dataset_id}.md", "w") as f:
        f.write(
            Template(dataset_showcase_template_j2).render(
                dataset=dataset_map[dataset_id],
                dataset_id=dataset_id,
            )
        )

with open(f"./docs/datasets/index.md", "w") as f:
    f.write(
        Template(dataset_index_template_j2).render(
            dataset_ids=dataset_ids,
            dataset_map=dataset_map,
        )
    )
