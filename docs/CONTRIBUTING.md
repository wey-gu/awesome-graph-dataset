## Contribution Guide

### Adding a new dataset

To contribute a new dataset to the Graph Dataset Hub, please follow these steps:

1. **Issue a PR**: Before adding a new dataset, [open an issue](https://github.com/wey-gu/awesome-graph-dataset/issues){ .md-button } detailing the dataset you wish to add. This allows for discussion and collabration before moving forward.

2. **Dataset Introduction**: Once the issue is approved, you can proceed with introducing the dataset by following the steps outlined below.

- Create a folder in the `datasets` directory with the id of the dataset.
- Add a `metadata.yaml` file in the dataset folder.
- Add a `schema.ddl.ngql` file in the dataset folder.
- Add `nav` in the `mkdocs.yml` file, in alphabetical order.
- Add dataset CSV files in the dataset folder, with git LFS enabled, at least the tiny profile.
