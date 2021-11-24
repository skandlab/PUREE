# PUREE

PUREE is a compact and fast method for predicting purity (cancer cell fraction) from gene expression data.

## Input

For the input, PUREE requires a gene expression matrix. The normalization space can be potentially anything - from FPKM and TPM, to counts and microarray data. The matrix has to be oriented with samples as rows and genes as columns (*[samples, features]* shape). The gene ids can be in either HGNC or ENSEMBL nomenclature.

## Output

As an output, PUREE will return tumor purity values per every sample in the input gene expression matrix.

## Running PUREE

To run PUREE, you will need an access to UNIX-like command line and a Python 3 environment (ideally Python 3.7+). Additionally, you may need to install several dependencies.

### Dependencies

The dependencies list for PUREE is really short and consists of Python 3 and packages

```
scikit-learn
numpy
pandas
joblib
```

You can either install those manually, or run the command below to install all of them at once with pip:

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
		  	 [--gene_identifier_type {HGNC,ENSEMBL}]  # optional argument to specify gene id nomenclature
```

*Note:* PUREE was tested using Python 3 environment on Ubuntu 18 and Windows 10, and should generally run on all platforms. If you are using old version of the dependencies you might run into soft warnings, but the method will still return correct values.

### Example usage

Included with the package there are a couple of data sets as a sample for how to run PUREE. They are not needed for the package to run and only included as a test data. You can use the commands below to check whether the installation worked as intended.

```shell
 # Chen et. al lung cancer data, ENSEMBL_ID gene labels (see PUREE manuscript for details)
 python3 predict_purity.py --data_path data/test_data/Chen_et_al_norm_TPM_ENSG.tsv \
 		 	   --output data/test_data/Chen_et_al_norm_TPM_ENSG_purities.tsv
```

```shell
  # Kim et. al gastric cancer data, HNGC gene labels (see PUREE manuscript for details)
 python3 predict_purity.py --data_path data/test_data/Kim_et_al_FPKM.tsv \
 			   --output data/test_data/Kim_et_al_FPKM_purities.tsv \
 			   --gene_identifier_type HGNC
```

## Acknowledgements

PUREE is developed by Egor Revkov in the lab of Computational Cancer Genomics of Anders Skanderup at the Genome Institute of Singapore.

PUREE is released under the Academic Free License and is free to use for academic research, but please cite it if you are using the method's results in your work. If you wish to use the method in the commercial application, contact the author at revkov.egor [at] gmail.com.

If you have an issue running the method, feel free to raise an issue in this repository or write to the author of the package at the email mentioned above.
