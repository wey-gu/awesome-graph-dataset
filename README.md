<a href="https://graph-hub.siwei.io"><img src="https://github.com/wey-gu/awesome-graph-dataset/assets/1651790/2f7f5c79-ff36-4fb7-9a41-bd36932f7a32" alt="Awesome Graph Dataset Banner" width="20%"></a>

## Awesome Graph Dataset

[Graph Hub](https://graph-hub.siwei.io) is a community and site, to gether selected collection of graph datasets tailored for NebulaGraph.

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
