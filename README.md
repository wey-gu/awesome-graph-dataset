
<picture>
  <img style="width: 60%; margin-left: auto; margin-right: auto; display: block;" alt="Graph Hub Banner" src="https://github.com/wey-gu/awesome-graph-dataset/assets/1651790/2f7f5c79-ff36-4fb7-9a41-bd36932f7a32">
</picture>

<p align="center">
    <em>Graph Data in One Click</em>
</p>

## Awesome Graph Dataset

[Graph Hub](https://graph-hub.siwei.io) is an Open Source community and hub, providing a carefully selected assortment of graph datasets tailored for [NebulaGraph](https://github.com/vesoft-inc/nebula).

You could explore Graph Query, Algorithm, Visualization, GNN, GenAI(Graph RAG) and more by copy & paste the ingestion commands from the dataset page.

## How to use

### Load Data within Jupyter Notebook

```python
!pip install jupyter-nebulagraph
%load_ext ngql
```

Option 0(Not yet supported):
> TBD for integration with Juypter-NebulaGraph.

```python
%ng_dataset supply_chain
```

Option 1:

Load with `%ng_load` magic command to load data from registry of Graph Dataset Hub.

- See [supply_chain dataset download](https://graph-hub.siwei.io/en/latest/datasets/supply_chain/#__tabbed_4_2) for more details.
- See [%ng_load magic command](https://jupyter-nebulagraph.readthedocs.io/en/latest/magic_words/ng_load/) for command usage.

```python
%ng_load --header --source https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/supply_chain/tiny/nodes_car_model.csv --tag car_model --vid 0 --props 1:name,2:number,3:year,4:type,5:engine_type,6:size,7:seats --space supply_chain
%ng_load --header --source https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/supply_chain/tiny/nodes_feature.csv --tag feature --vid 0 --props 1:name,2:number,3:type,4:state --space supply_chain
%ng_load --header --source https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/supply_chain/tiny/nodes_part.csv --tag part --vid 0 --props 1:name,2:number,3:price,4:date --space supply_chain
%ng_load --header --source https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/supply_chain/tiny/nodes_supplier.csv --tag supplier --vid 0 --props 1:name,2:address,3:contact,4:phone_number --space supply_chain
%ng_load --header --source https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/supply_chain/tiny/with_feature.csv --edge with_feature --src 0 --dst 1 --props 2:version --space supply_chain
%ng_load --header --source https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/supply_chain/tiny/is_composed_of.csv --edge is_composed_of --src 0 --dst 1 --props 2:version --space supply_chain
%ng_load --header --source https://github.com/wey-gu/awesome-graph-dataset/raw/main/datasets/supply_chain/tiny/is_supplied_by.csv --edge is_supplied_by --src 0 --dst 1 --props 2:version --space supply_chain
```

### Load Data within NebulaGraph Console

> TBD for integration with NebulaGraph Console

```shell
:play supply_chain
```

### Load Data with NebulaGraph Importer

```shell
# run the importer
docker run --rm -ti \
    -v ${PWD}/data/supply_chain/:/data \
    -v ${PWD}/importer_v4_config.yaml:/root/importer_v4_config.yaml \
    vesoft/nebula-importer:v4 \
    -c /root/importer_v4_config.yaml
```

See more per each dataset in [Graph Dataset Hub](https://graph-hub.siwei.io/).

## Contributing

Please refer to the [Contribution Guide](https://graph-hub.siwei.io/en/latest/CONTRIBUTING/) for more information on how to introduce new datasets to the Graph Dataset Hub.
