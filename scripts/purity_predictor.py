import sys

import numpy as np
import pandas as pd
from joblib import load

class PurityPredictor:
    """
    Tumor purity predictor class with the collection of respective functions
    """

    def __init__(self):
        self.data = pd.DataFrame()
        self.purities = pd.DataFrame()

        self._genes_names_conversion_df = pd.DataFrame()
        self._model = None

    def read_data(self, data_path):
        """
        Reads data into the memory
        """
        if data_path.split(".")[-1] == 'csv':
            self.data = pd.read_csv(data_path, index_col=0)
        elif data_path.split(".")[-1] == 'tsv':
            self.data = pd.read_csv(data_path, index_col=0, sep='\t')
        else:
            sys.exit('ERROR: Unsupported data format, exiting... '
                     '(Input matrix has to be either in .csv or .tsv)')

        # check if the shape is what we expect: samples x genes
        # if there are many more rows than columns, transpose the data
        if (len(self.data.index) > len(self.data.columns)*100) | ((len(self.data.index) >= 10000) & (len(self.data.columns) <= 5000)):
            print('Looks like genes are supplied as rows instead of columns, transposing')
            self.data = self.data.T

    def clean_data(self, genes_names_conversion_df_path, ranking_universe_genes, fill_value=np.nan, input_ids='HGNC'):
        """
        Cleans the data:
            - converts gene names into ENSEMBL IDs from HGNC gene symbols
            - finds an intersection of the genes in the provided matrix with the ranking universe and only keeps them
        """
        self._genes_names_conversion_df = pd.read_csv(genes_names_conversion_df_path, index_col=0)

        data = self.data 

        if input_ids == 'HGNC':

            conv_df = (self._genes_names_conversion_df[self._genes_names_conversion_df['ENSEMBL_ID'].isin(ranking_universe_genes)]
                        .set_index('HGNC')
                        .loc[:, ['ENSEMBL_ID']]
                        .drop_duplicates())
                        
            data = data.reindex(conv_df.index, axis=1, fill_value=fill_value)
            data.columns = conv_df['ENSEMBL_ID']
            data = data.reindex(ranking_universe_genes, axis=1, fill_value=fill_value)
            
        elif input_ids == 'ENSEMBL':
            data = data.reindex(labels=ranking_universe_genes, axis=1, fill_value=fill_value)

        self.data = data

    def filter_genes(self, genes_to_keep=None):
        """
        Keeps only specified genes in the dataset
        """
        columns_to_keep = self.data.columns.intersection(genes_to_keep, sort=None)
        self.data = self.data.loc[:, columns_to_keep]

    def rank_normalize_data(self, rank_method='min'):
        """
        Perform rank-transformation: rank the genes, so that the highest expression value in a sample
        would have the highest rank
        """
        self.data = self.data.rank(axis=1, method=rank_method, pct=True)

    def predict_purities(self, model_path):
        """
        Predict purities using a pre-trained model
        """
        self._model = load(model_path)
        self._predict_sklearn_like()

    def _predict_sklearn_like(self):
        """
        Predicts purities using sklearn methods
        """
        model = self._model
        data = self.data

        purities = model.predict(data)
        purities_df = pd.DataFrame(
            purities, index=data.index, columns=['purity'])

        self.purities = purities_df