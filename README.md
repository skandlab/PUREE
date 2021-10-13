# PUREE

PUREE is a compact and fast method for predicting purity (cancer cell fraction) from gene expression data.

## Input

For the input, PUREE requires a gene expression matrix. The normalization space can be potentially anything - from FPKM and TPM, to counts and microarray data. The matrix has to be oriented with samples as rows and genes as columns (*[samples, features]* shape). The gene ids can be in either HGNC or ENSEMBL ids.

## Output

As an output, PUREE will return tumor purity values per every sample in the input gene expression matrix.

## Running PUREE

To run PUREE, you will need an access to UNIX-like command line and a Python 3 environment. Additionally, you may need to install several dependencies.

### Dependencies

The dependencies list for PUREE is really short and consists of Python 3 and packages

```
sklearn
numpy
pandas
joblib
```

You can either install those manually, or run

```shell
pip install -r requirements.txt 
```

### Running in command line

To run PUREE in command line, clone the github repository to your machine

```shell
gh repo clone skandlab/PUREE
cd PUREE
```

 and run PUREE prediction with

```shell
python3 predict_purity.py --data_path input_matrix_path \
			  --output output_path \
		  	 [--gene_identifier_type {HGNC,ENSEMBL}]  # optional argument to specify gene id nomenclature
```

### Example usage

Included there are a couple of datasets as a sample on how to run PUREE

```shell
 # Chen et. al lung cancer data (see PUREE manuscript for details)
 python3 predict_purity.py --data_path data/test_data/Chen_et_al_norm_TPM_ENSG.tsv \
 		 	   --output data/test_data/Chen_et_al_norm_TPM_ENSG_purities.tsv
```

```shell
  # Kim et. al gastric cancer data (see PUREE manuscript for details)
 python3 predict_purity.py --data_path data/test_data/Kim_et_al_FPKM.tsv \
 			   --output data/test_data/Kim_et_al_FPKM_purities.tsv
```

## Acknowledgements

PUREE is developed by Egor Revkov in the lab of Computational Cancer Genomics of Anders Skanderup at the Genome Institute of Singapore.

PUREE is free to use for academic research, but please cite it if you are using the method's results in your work.

If you have an issue running the method, feel free to raise an issue in this repository or write to the author of the package at revkov.egor [at] gmail.com 
