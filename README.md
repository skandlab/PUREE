# PUREE (Python API)

## Introduction
PUREE is a compact and fast method for predicting tumor purity (cancer cell fraction) from bulk gene expression data. The methodology and the validation process is described in the paper [PUREE: accurate pan-cancer tumor purity estimation from gene expression data](https://doi.org/10.1038/s42003-023-04764-8). PUREE is also available as a web service at [https://puree.genome.sg](https://puree.genome.sg). If you would like an access to the PUREE's backend code, please contact the corresponding author of the paper.

The PUREE class is a wrapper class that exposes functionality to interact with the PUREE code. The class allows you to monitor the health of the backend, submit a file for processing, and get the logs and puree-processed output.

## Requirements
This package has the following dependencies

```
pandas==1.5.3
requests==2.28.2
```



## Installing and running PUREE
To install PUREE, run

1. git clone https://github.com/skandlab/PUREE
2. cd PUREE
3. python3 setup.py bdist_wheel
4. pip install dist/PUREE-0.1.0-py3-none-any.whl --force-reinstall # this can be installed in the environment of your choice

Now you can use PUREE in your Python environment:

```
from puree import *

p = PUREE()
purities_and_logs = p.get_output(test_data_path, gene_id_nomenclature)
```
where

| variable             | description                                                  |
| -------------------- | ------------------------------------------------------------ |
| test_data_path       | string; path to the gene expression matrix in .tsv, .csv or .parquet |
| gene_id_nomenclature | string; gene ids nomenclature: 'ENSEMBL' or 'HGNC'           |



## Input

PUREE expects a gene expression matrix as input, in any normalization space, preferably oriented with genes as columns and samples as rows. Gene IDs are accepted in either HGNC or ENSEMBL nomenclature.

More specifically, the expected input would schematically look like this

|                 | gene_id_1 | gene_id_2 |
| --------------- | --------- | --------- |
| **sample_id_1** | 10        | 1         |
| **sample_id_2** | 0         | 10        |



## Output
The output of PUREE is a .tsv file with tumor purities in the first column along with any logs that puree generates.
Example:
{"output": purity dataframe, "logs": PUREE logs}
_Note: the sample names will be anonymized. However, the purities are returned in the same order as the samples in the input._

