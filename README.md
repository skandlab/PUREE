# PUREE (Python API)

## Introduction
PUREE is a compact and fast method for predicting tumor purity (cancer cell fraction) from bulk gene expression data. The methodology and the validation process is described in the preprint Accurate pan-cancer tumor purity estimation from gene expression data [https://www.biorxiv.org/content/10.1101/2022.06.01.494462v1]. PUREE is also available as a web service here [https://puree.genome.sg].

The Puree class is a wrapper class that exposes functionality to interact with the PUREE code. The class allows you to monitor the health of the backend, submit a file for processing, and get the logs and puree-processed output.

## Requirements
The following packages need to be installed to run this code:

cProfile
requests
time
os
pandas

## Installing and running PUREE
To install PUREE, run

1. git clone https://github.com/skandlab/PUREE
2. cd PUREE
3. python setup.py bdist_wheel
4. pip install dist/puree-0.1.0-py3-none.any.whl --force-reinstall # this can be installed in the environment of your choice

Now you can use PUREE in your Python environment:

```
from puree_api import *

p = PUREE()
purities = p.get_output(test_data_path, gene_id_nomenclature, email)
```
where

variable	description

test_data_path	string; path to the gene expression matrix in .tsv, .csv or .parquet
gene_id_nomenclature	string; gene ids nomenclature: 'ENSEMBL' or 'HGNC
email	string; your academic email

## Input

PUREE expects a gene expression matrix as input, in any normalization space, preferably oriented with genes as columns and samples as rows. Gene IDs are accepted in either HGNC or ENSEMBL nomenclature. We additionally require an institute-associated (academic) email to be provided with the job submission.

More specifically, the expected input would schematically look like this

            gene_id_1	gene_id_2
sample_id_1      10      	1
sample_id_2	     0	        10

## Output
The output of PUREE is a .tsv file with tumor purities in the first column along with any logs that puree generates.

_Note: the sample names will be anonymized. However, the purities are returned in the same order as the samples in the input._

