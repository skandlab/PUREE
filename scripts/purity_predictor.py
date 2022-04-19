import sys

import numpy as np
import pandas as pd
from joblib import load

from scripts import utils


class PurityPredictor:
    """
    A collection of methods for predicting tumor purities.
    """

    def __init__(self):
        self.data = pd.DataFrame()
        self.purities = pd.DataFrame()

        # internal variables
        self._genes_names_conversion_df = pd.DataFrame()
        self._training_genes_names_df = pd.DataFrame()
        self._scaler = np.nan
        self._model = np.nan

    def read_data(self, data_path):
        """
        Reads data into the memory .
        """
        if data_path.split(".")[-1] == 'parquet':
            self.data = pd.read_parquet(data_path, engine='pyarrow')
        elif data_path.split(".")[-1] == 'csv':
            self.data = pd.read_csv(data_path, index_col=0)
        elif data_path.split(".")[-1] == 'tsv':
            self.data = pd.read_csv(data_path, index_col=0, sep='\t')
        else:
            sys.exit('ERROR: Unsupported data format, exiting... '
                     '(Input matrix has to be .csv, .tsv or .parquet)')

        # check if the shape is what we expect: samples x genes
        # if there are many more rows than columns, transpose the data
        if (len(self.data.index) > len(self.data.columns)*100) | ((len(self.data.index) >= 10000) & (len(self.data.columns) <= 5000)): # hardcoded matrix orientation check
            print('Looks like genes are supplied as rows instead of columns, transposing')
            self.data = self.data.T

    def clean_data(self, genes_names_conversion_df_path, training_genes_names, fill_value=np.NaN, input_ids='HGNC'):
        """
        Cleans the data:
            - converts gene names into ENS IDs from HGNC IDs
            - finds an intersection with the list of genes used during training and only keeps them
        """
        # loading genes names into the memory
        self._genes_names_conversion_df = pd.read_csv(genes_names_conversion_df_path, index_col=0)
        # self._training_genes_names_df = pd.read_csv(training_genes_names_path)

        data = self.data  # pointer to data

        if input_ids == 'HGNC':
            # step 1: leave only columns from the gene conversion table
            data = data.loc[:, data.columns.isin(
                self._genes_names_conversion_df['HGNC'])]
            # step 2: convert the columns' names into ENS ID
            # data.columns = genes_names_conversion_df.set_index('HGNC').loc[data.columns, :]['ENSEMBL_ID']
            conv_df = (self._genes_names_conversion_df[['ENSEMBL_ID', 'HGNC']].set_index('HGNC')
                  .loc[data.columns]
                  .drop_duplicates())
            # the next line is to filter out duplicate ENSEMBL_IDs for certain HGNCs
            data.columns = conv_df.groupby(conv_df.index).first().loc[data.columns]['ENSEMBL_ID']
            # step 3: select all training genes
            data = data.reindex(labels=training_genes_names, axis=1, fill_value=fill_value)
        elif input_ids == 'ENSEMBL':
            # step 3: keep only the genes that were used for training
            data = data.reindex(labels=training_genes_names, axis=1, fill_value=fill_value)

        self.data = data

    def filter_gene_expression(self,
                               mode='keep_list',
                               genes_to_keep=None,
                               expression_cutoff=0.9,
                               n_var_genes=250):
        """
        Keeps only specified genes in the dataset.
        """

        if mode == 'keep_list':
            # keep only the genes supplied in the list
            columns_to_keep = self.data.columns.intersection(genes_to_keep, sort=None)  # intersect first
            self.data = self.data.loc[:, columns_to_keep]

        # elif mode == 'fpkm_filter':
        #     # keep only the genes that are expressed above the specified cutoff
        #     self.gene_expression = utils.filter_by_fpkm(self.gene_expression,
        #                                                 expression_cutoff=expression_cutoff)
        #
        # elif mode == 'var_genes':
        #     # keep only the specified number of the most variant genes
        #     self.gene_expression = utils.select_n_var_genes(self.gene_expression,
        #                                                     n_var_genes=n_var_genes)

    def rank_normalize_data(self, mode='linear', rank_method='average'):
        """
        Rank-normalizes the data.
        """
        self.data = utils.rank_transform(self.data, mode=mode, rank_method=rank_method)

    def standartize_data(self, scaler_path):
        """
        Standardizes the data using a pre-trained scaler.
        """

        self._scaler = load(scaler_path)
        data = self.data

        cols = data.columns.values
        inds = data.index.values

        # applying the old scaler to the new data
        data_st_val = self._scaler.transform(data)
        data_st_df = pd.DataFrame(data_st_val, index=inds, columns=cols)

        self.data = data_st_df

    def predict_purities(self, model_path):
        """
        Predict purities using a pre-trained model. Tries to infer which
        compression format was used to save the model and uses an appropriate function to unpack it.
        """
        if model_path.split(".")[-1] == 'joblib':
            # sklearn models
            self._model = load(model_path)
            self._predict_sklearn_like()
        elif model_path.split(".")[-1] == 'h5':
            # Keras models
            self._model = load_model(model_path)
            self._predict_sklearn_like()
        elif model_path.split(".")[-1] == 'pth':
            # fastai models
            # TODO: update it for fastai models
            pass
        else:
            self._model = load(model_path)

    def _predict_sklearn_like(self):
        """
        Predicts purities using sklearn methods, saves them in the internal memory (self)
        """
        model = self._model
        data = self.data

        # purities = model.predict(data.values)
        purities = model.predict(data) # include feature names for the new version of sklearn
        purities_df = pd.DataFrame(
            purities, index=data.index, columns=['purity'])

        self.purities = purities_df
