import sys
import argparse

import pandas as pd
import numpy as np
from joblib import load
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

from scripts.purity_predictor import PurityPredictor

# constants
GENES_IDENTIFIERS_CONVERSION_TABLE_PATH = "data/ENSG_ENST_HGNC_conversion_table.csv"

SIGNIFICANTLY_EXPRESSED_GENES_PATH = "data/significantly_expressed_genes.csv"
SELECTED_GENES_LIST_PATH = "data/selected_genes.csv"

SELECTED_GENES_MODEL_PATH = "models/pancancer/Lasso_log-rt_170.joblib"
SIGNIFICANT_GENES_MODEL_PATH = "models/pancancer/Lasso_log-rt_10000.joblib"

STANDARD_SCALER_SELECTED_GENES_PATH = "models/pancancer/standard_scaler_pancancer_log-rt_170.joblib"
STANDARD_SCALER_10000_GENES_PATH = "models/pancancer/standard_scaler_pancancer_log-rt_10000.joblib"

VALUES_IMPUTER_PATH = 'models/pancancer/imputer_170.joblib'
RANDOM_STATE = 93  # for the imputation reproducibility

VARIANCE_THRESHOLD = 1.00015 # determined based on TCGA-train split

# parsing the arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Predicting tumor purity (cancer cell fraction) with PUREE')

    parser.add_argument('--data_path', type=str, required=True,
                        help='Path to gene expression matrix of size [samples, genes]')
    parser.add_argument('--output', type=str, required=True,
                        help='Output file path')
    parser.add_argument('--gene_identifier_type', type=str,
                        choices=['HGNC', 'ENSEMBL'], default='ENSEMBL',
                        help='Gene Identifier type (e.g. HGNC, ENSEMBL)')
    parser.add_argument('--run_mode', type=str,
                        choices=['PUREE_genes', '10000_significant_genes'], default='PUREE_genes',
                        help='Gene set used for predicting purities')

    return parser.parse_args()


def main():
    args = parse_args()

    data_path = args.data_path
    gene_identifier_type = args.gene_identifier_type
    run_mode = args.run_mode
    output_path = args.output

    genes_identifiers_conversion_table_path = GENES_IDENTIFIERS_CONVERSION_TABLE_PATH
    selected_genes_list = pd.read_csv(SELECTED_GENES_LIST_PATH)['ENSEMBL_ID']
    significantly_expressed_genes = pd.read_csv(SIGNIFICANTLY_EXPRESSED_GENES_PATH)['ENSEMBL_ID']

    # checking which gene set are we using
    if run_mode == 'PUREE_genes':
        model_path = SELECTED_GENES_MODEL_PATH
        standard_scaler_path = STANDARD_SCALER_SELECTED_GENES_PATH

        # arguments for the imputation
        values_imputer = load(VALUES_IMPUTER_PATH)

    print('Reading data from %s' % data_path)
    predictor = PurityPredictor()
    predictor.read_data(data_path=data_path)
    predictor.clean_data(genes_identifiers_conversion_table_path, significantly_expressed_genes,
                         input_ids=gene_identifier_type)
    predictor.data.loc[:, predictor.data.sum() == 0] = np.NaN  # remove genes with 0 variation
    predictor.rank_normalize_data(mode='log', rank_method='max')  # log-rank first, filter for the smaller list later
    predictor.filter_gene_expression('keep_list', selected_genes_list)
    predictor.standartize_data(standard_scaler_path)
    print('Reading data finished')

    # taking note of which genes are missing
    genes_na = np.intersect1d(predictor.data.columns[pd.isna(predictor.data.var())],
                              selected_genes_list)
    # print('%s missing genes' % len(genes_na), *genes_na)  # reducing verbocity

    if len(genes_na) == predictor.data.columns.shape[0]:
        sys.exit('ERROR: All of the selected genes are missing from the data, exiting... '
                 '(Did you set correct gene identifier type (HNGC or ENSEMBL)?)')

    # missing values imputation
    print('Starting imputation...')

    var_th = VARIANCE_THRESHOLD
    predictor.data.loc[:, predictor.data.var() > 3 * var_th] = np.NaN  # removing suspiciously high values

    imputed_values = values_imputer.transform(predictor.data)
    to_predict_imputed = pd.DataFrame(imputed_values, index=predictor.data.index, columns=predictor.data.columns)
    predictor.data = to_predict_imputed
    print('Imputation finished')

    # predicting purities
    print('Predicting...')
    predictor.predict_purities(model_path)
    purity = predictor.purities
    purity.loc[purity.purity < 0, :] = 0  # cutting negative values
    purity.loc[purity.purity > 1, :] = 1  # cutting high values
    print('Prediction finished')

    print('Saving predicted purities')
    purity.to_csv(output_path, sep='\t')


if __name__ == '__main__':
    main()
