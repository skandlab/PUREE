import sys
import argparse

# ignore sklearn's versioning warnings
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

import pandas as pd
import numpy as np
from joblib import load

from scripts.purity_predictor import PurityPredictor

# constants
GENES_IDENTIFIERS_CONVERSION_TABLE_PATH = "data/gene_id_conversion_table.csv"

RANKING_UNIVERSE_LIST_PATH = "data/ranking_universe.csv"
PREDICTIVE_GENES_LIST_PATH = "data/predictive_genes.csv"

MODEL_PATH = "models/model.joblib"

VALUES_IMPUTER_PATH = 'models/median_imputer.joblib'

# parsing the arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Predicting tumor purity (cancer cell fraction) with PUREE')

    parser.add_argument('--data_path', type=str, required=True,
                        help='Path to gene expression matrix of size [samples, genes]')
    parser.add_argument('--output', type=str, required=True,
                        help='Output file path')
    parser.add_argument('--gene_identifier_type', type=str,
                        choices=['HGNC', 'ENSEMBL'], default='ENSEMBL',
                        help='Gene identifier type (e.g. HGNC symbols, or ENSEMBL IDs)')

    return parser.parse_args()


def main():
    args = parse_args()

    data_path = args.data_path
    gene_identifier_type = args.gene_identifier_type
    output_path = args.output

    genes_identifiers_conversion_table_path = GENES_IDENTIFIERS_CONVERSION_TABLE_PATH
    selected_genes_list = pd.read_csv(PREDICTIVE_GENES_LIST_PATH)['ENSEMBL_ID']
    significantly_expressed_genes = pd.read_csv(RANKING_UNIVERSE_LIST_PATH)['ENSEMBL_ID']

    model_path = MODEL_PATH

    values_imputer = load(VALUES_IMPUTER_PATH)

    print('Reading data from %s' % data_path)

    predictor = PurityPredictor()
    predictor.read_data(data_path=data_path)
    predictor.clean_data(genes_identifiers_conversion_table_path, significantly_expressed_genes,
                         input_ids=gene_identifier_type)

    predictor.rank_normalize_data(rank_method='min') 

    predictor.filter_genes(selected_genes_list)
    
    print('Loading data finished')

    # checking how many genes from the predictive set are missing
    genes_na = np.intersect1d(predictor.data.columns[pd.isna(predictor.data.sum(skipna=False))],
                              selected_genes_list)
 
    if len(genes_na) == predictor.data.columns.shape[0]:
        sys.exit('ERROR: All of the selected genes are missing from the data, exiting... '
                 '(Did you set correct gene identifier type (HGNC or ENSEMBL)?)')

    # missing values imputation
    print('Starting imputation...')

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
