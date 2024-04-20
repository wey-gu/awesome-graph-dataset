#!/usr/bin/env python3

# This tools parse NebulaGraph Importer Config YAML file and generate
# the corresponding command line arguments for %ng_load lines.

# This input example:
# ---
# version: v2
# clientSettings:
#   space: shareholding
# files:
#   - path: ./person.csv
#     failDataPath: ./err/person.csv
#     batchSize: 32
#     inOrder: true
#     type: csv
#     csv:
#       withHeader: false
#       withLabel: false
#     schema:
#       type: vertex
#       vertex:
#         vid:
#           index: 0
#         tags:
#           - name: person
#             props:
#               - name: name
#                 type: string
#                 index: 1
#               - name: birth_year
#                 type: int
#                 index: 5
#   - path: ./corp_share.csv
#     failDataPath: ./err/corp_share.csv
#     batchSize: 32
#     inOrder: false
#     type: csv
#     csv:
#       withHeader: true
#       withLabel: false
#     schema:
#       type: edge
#       edge:
#         name: hold_share
#         withRanking: true
#         srcVID:
#           index: 0
#         dstVID:
#           index: 1
#         rank:
#           index: 5
#         props:
#           - name: share
#             type: float
#             index: 2

# will generate the following output:

# %ng_load --source person.csv --tag person --vid 0 --props 1:name,5:birth_year --space shareholding
# %ng_load --header --source corp_share.csv --edge hold_share --src 0 --dst 1 --props 2:share --rank 5 --space shareholding

# Basically, it will parse information on:
# - edge or tag(of vertex) from files[].schema.type
# - source file name from files[].path
# - vertex id index if tag, or source and destination vertex id index if edge, from files[].schema.vertex.vid.index or files[].schema.edge.srcVID.index and files[].schema.edge.dstVID.index
# - edge rank index if exists, from files[].schema.edge.rank.index
# - edge properties and index mapping if exists, from files[].schema.edge.props[].name, files[].schema.edge.props[].index
# - properties and index mapping if exists, from files[].schema.vertex.tags[].props[].name, files[].schema.vertex.tags[].props[].index
# - header flag if exists, from files[].csv.withHeader
# - space name: from clientSettings.space

import requests
import yaml


def parse_vertex(schema: dict) -> tuple:
    """
    Parse the vertex schema and generate the vid and props string
    Args:
        schema: the vertex schema dictionary
    Returns:
        tuple: (vid: int, props: str)
    """
    try:
        vid = schema["vertex"]["vid"]["index"]
        if (
            len(schema["vertex"]["tags"]) == 1
            and "props" in schema["vertex"]["tags"][0]
        ):
            props = schema["vertex"]["tags"][0]["props"]
        else:
            props = []
    except KeyError as e:
        print(f"Error: Missing field {e} in the vertex schema: {schema}")
        return None
    props_str = ",".join([f"{p['index']}:{p['name']}" for p in props])
    return vid, props_str


def parse_edge(schema: dict) -> tuple:
    """
    Parse the edge schema and generate the src, dst, rank, and props string
    Args:
        schema: the edge schema dictionary
        rank: the rank index, if exists, -1 means no rank
    Returns:
        tuple: (src: int, dst: int, rank: int, props: str)
    """
    with_ranking = schema["edge"].get("withRanking", False)
    try:
        src = schema["edge"]["srcVID"]["index"]
        dst = schema["edge"]["dstVID"]["index"]
        rank = -1 if not with_ranking else schema["edge"]["rank"]["index"]
        if "props" in schema["edge"]:
            props = schema["edge"]["props"]
        else:
            props = []
    except KeyError as e:
        print(f"Error: Missing field {e} in the edge schema: {schema}")
        return None
    props_str = ",".join([f"{p['index']}:{p['name']}" for p in props])
    return src, dst, rank, props_str


def parse_file(file: dict, space: str) -> str:
    """
    Parse a file in the YAML field: files
    Generate the corresponding %ng_load line

    Args:
        file: the file dictionary in the YAML file
        space: the space name
    Returns:
        str: the corresponding %ng_load line
    """
    source = file["path"]
    # failDataPath = file['failDataPath']
    # batchSize = file['batchSize']
    # inOrder = file['inOrder']
    csv = file["csv"]
    schema = file["schema"]
    if schema["type"] == "vertex":
        parsed = parse_vertex(schema)
        if parsed is None:
            return None
        vid, props_str = parsed
        header = "--header" if csv["withHeader"] else ""
        props = f"--props {props_str}" if props_str else ""
        return f"%ng_load {header} --source {source} --tag {schema['vertex']['tags'][0]['name']} --vid {vid} {props} --space {space}"
    elif schema["type"] == "edge":
        parsed = parse_edge(schema)
        if parsed is None:
            return None
        src, dst, rank, props_str = parsed
        header = "--header" if csv["withHeader"] else ""
        props = f"--props {props_str}" if props_str else ""
        rank = f"--rank {rank}" if rank != -1 else ""
        return f"%ng_load {header} --source {source} --edge {schema['edge']['name']} --src {src} --dst {dst} {props} {rank} --space {space}"
    else:
        print(f"Error: Unknown schema type: {schema['type']}")
        return None


def validate_yaml(yaml_str: str) -> tuple:
    """
    Validate the YAML file, return the parsed data if valid, otherwise return None
    Result is tuple of (space, files)
    Args:
        yaml_str: the content of the YAML as a string
    Returns:
        tuple: (space: str, files: list) if valid, otherwise None
    """
    try:
        data = yaml.load(yaml_str, Loader=yaml.FullLoader)
    except yaml.YAMLError as e:
        print(f"Error: {e}")
        return None

    # Validation on schema
    if "version" not in data:
        print("Error: Missing version field in the YAML file")
        return None
    if "clientSettings" not in data:
        print("Error: Missing clientSettings field in the YAML file")
        return None
    if "space" not in data["clientSettings"]:
        print("Error: Missing space field in the clientSettings")
        return None
    if "files" not in data:
        print("Error: Missing files field in the YAML file")
        return None
    for file in data["files"]:
        if "path" not in file:
            print("Error: Missing path field in the file")
            return None
        if "schema" not in file:
            print("Error: Missing schema field in the file")
            return None
        if "type" not in file["schema"]:
            print("Error: Missing type field in the schema")
            return None
        if file["schema"]["type"] == "vertex":
            if "vertex" not in file["schema"]:
                print("Error: Missing vertex field in the schema")
                return None
            if "tags" not in file["schema"]["vertex"]:
                print("Error: Missing tags field in the vertex")
                return None

            if len(file["schema"]["vertex"]["tags"]) != 1:
                print("Error: Only one tag is supported for vertex")
                return None
            if "props" not in file["schema"]["vertex"]["tags"][0]:
                print(
                    f"Warn: tag: {file['schema']['vertex']['tags'][0]['name']} is propless"
                )
            if "name" not in file["schema"]["vertex"]["tags"][0]:
                print("Error: Missing name field in the tag")
                return None

        elif file["schema"]["type"] == "edge":
            if "edge" not in file["schema"]:
                print("Error: Missing edge field in the schema")
                return None
            if "props" not in file["schema"]["edge"]:
                print(f"Warn: edge: {file['schema']['edge']['name']} is propless")
            if "name" not in file["schema"]["edge"]:
                print("Error: Missing name field in the edge")
                return None

    return data["clientSettings"]["space"], data["files"]


def parse_yaml(yaml_path_or_url: str) -> list:
    """
    Parse the YAML file and generate the corresponding %ng_load lines

    Args:
        yaml_path_or_url: the path to the YAML file, could be a path or a URL

    Returns:
        list: the list of %ng_load lines
    """
    try:
        if yaml_path_or_url.startswith("http"):
            response = requests.get(yaml_path_or_url)
            if response.status_code != 200:
                print(
                    f"Error: Failed to download the YAML file from {yaml_path_or_url}"
                )
                return []
            yaml_str = response.text
        else:
            with open(yaml_path_or_url, "r") as f:
                yaml_str = f.read()
    except Exception as e:
        print(f"Error: failed to read the YAML file: {e}")
        return []
    parsed = validate_yaml(yaml_str)
    if parsed is None:
        raise ValueError("Invalid YAML file")

    space, files = parsed
    success_lines = []
    fail_lines = []
    for file in files:
        line = parse_file(file, space)
        if line is None:
            fail_lines.append(str((file["path"], file["schema"]["type"])))
        else:
            success_lines.append(line)
    if fail_lines:
        print(
            f"Failed to generate %ng_load lines for the following files: {', '.join(fail_lines)}"
        )
    return success_lines


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse NebulaGraph Importer Config YAML file and generate the corresponding command line arguments for %ng_load lines"
    )
    parser.add_argument(
        "yaml_path_or_url",
        type=str,
        help="The path to the YAML file, could be a path or a URL",
    )
    args = parser.parse_args()

    print(f"YAML file: {args.yaml_path_or_url}")
    print("")
    print("Parsed %ng_load lines:")

    lines = parse_yaml(args.yaml_path_or_url)

    print("\n".join(lines))
    print("")

