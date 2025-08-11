# PUREE (v1.0) 

PUREE is a compact and fast method for predicting tumor purity (cancer cell fraction) from bulk gene expression data. The methodology and the validation process is described in the publication [PUREE: accurate pan-cancer tumor purity estimation from gene expression data](https://doi.org/10.1038/s42003-023-04764-8).

## Input

For the input, PUREE requires a gene expression matrix in the .csv or .tsv format. The normalization space can be potentially anything - from FPKM and TPM, to counts and microarray data. Preferably, the matrix has to be oriented with samples as rows and genes as columns (*[samples, features]* shape), although the method will try to check the orientation. The gene identifiers can be passed as either ENSEMBL IDs (default) or HGNC symbols.

## Output

As an output, PUREE will return tumor purity values per every sample in the input gene expression matrix.

## Running PUREE

To run PUREE, you will need an access to UNIX-like command line and a Python 3.8+ environment. Additionally, you may need to install several dependencies.

### Dependencies

The dependencies list for PUREE consists of the following Python packages:

```
scikit-learn==1.1.2
numpy==1.23.2
pandas==1.4.3
joblib==1.1.0
```

You can either install those manually one by one, use a pre-cofigured conda environment, or run the command below to install all of them at once with pip:

```shell
pip3 install -r requirements.txt 
```

### Running in command line

To download PUREE, simply clone the GitHub repository to your machine (you might need to install [GitHub CLI](https://cli.github.com/) first):

```shell
gh repo clone skandlab/PUREE # downloads the package
cd PUREE # moves into the installation directory
```

 To run PUREE in command line, run the following command from inside the installation directory:

```shell
# run from inside the installation directory
python3 predict_purity.py --data_path input_matrix_path \
			  			  --output output_path \
		  	 			 [--gene_identifier_type {HGNC,ENSEMBL}]  # optional argument to specify gene id nomenclature; default: ENSEMBL
```

*Note:* PUREE was tested using Python 3 environment on Ubuntu 18 and Windows 10, and should generally run on all platforms. If you are using older version of the dependencies you might run into soft warnings, but the method will still return correct values.

### Example usage

Example commands to run PUREE would be

```shell
 # for ENSEMBL IDs
 python3 predict_purity.py --data_path data.csv \
 		 	   			   --output purities.tsv
```

```shell
  # for HGNC symbols
 python3 predict_purity.py --data_path data.csv \
 			  			   --output purities.tsv \
 			   			   --gene_identifier_type HGNC
```

### Tests

The /tests directory contains a simple test dataset (based on a few samples of [TCGA PCPG data](https://xenabrowser.net/datapages/?dataset=TCGA-PCPG.htseq_fpkm.tsv&host=https%3A%2F%2Fgdc.xenahubs.net&removeHub=https%3A%2F%2Fxena.treehouse.gi.ucsc.edu%3A443)) and the precomputed purities to check whether your installation works as intended. Predict the test purities using the following:

```shell
python3 predict_purity.py --data_path tests/expression.tsv \
						  --output tests/purities_predicted.tsv	  
```

## License
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.<br /><br /><a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>

---
---
**Deprecated, August 2025**

# PUREE v1.0.0 (Python API)

## Introduction
PUREE is a compact and fast method for predicting tumor purity (cancer cell fraction) from bulk gene expression data. The methodology and the validation process is described in the paper [PUREE: accurate pan-cancer tumor purity estimation from gene expression data](https://doi.org/10.1038/s42003-023-04764-8).

The PUREE class is a wrapper class that exposes functionality to interact with the PUREE code. The class allows you to monitor the health of the backend, submit a file for processing, and get the logs and the output.

## Requirements
This package is tested on Python versions above `3.8`. In addition, it has the following dependencies

```
pandas==1.5.3
requests==2.28.2
```

## Installing and running PUREE
To install PUREE, run the following in the command line:

```bash
git clone https://github.com/skandlab/PUREE
cd PUREE
python3 setup.py bdist_wheel
pip install dist/PUREE-0.1.0-py3-none-any.whl --force-reinstall # this can be installed in the environment of your choice
```

Now you can use PUREE in your Python environment:

```Python3
from puree import *

p = PUREE()
purities_and_logs = p.get_output(test_data_path, gene_id_nomenclature)
```
where

| variable             | description                                                  |
| -------------------- | ------------------------------------------------------------ |
| test_data_path       | string; path to the gene expression matrix in .csv or .tsv|
| gene_id_nomenclature | string; gene ids nomenclature: 'ENSEMBL' or 'HGNC'           |



## Input

PUREE expects a gene expression matrix as input, in any normalization space, preferably oriented with genes as columns and samples as rows. The gene identifiers can be passed as either ENSEMBL IDs or HGNC gene symbols.

More specifically, the expected input would schematically look like this

|                 | gene_id_1 | gene_id_2 |
| --------------- | --------- | --------- |
| **sample_id_1** | 10        | 1         |
| **sample_id_2** | 0         | 10        |



## Output
PUREE returns a .tsv file with tumor purities in the first column. The output and the logs are stored in a dictionary: {"output": purity_dataframe, "logs": PUREE_logs}.  
_Note: the sample names will be anonymized. However, the purities are returned in the same order as the samples in the input._

