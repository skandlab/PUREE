import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def filter_by_fpkm(gene_expr_df, expression_cutoff=0.9):
    """
        Input: gene expression matrix
        Returns: gene expression matrix with less genes

        Leave genes with log2(fpkm+0.001) > 1 in [fpkm_cutoff] portion of samples, drop the rest
        (the assumption is that for purity estimation it is important to get genes which
        are significantly expressed in most samples).
    """

    genes_prop = gene_expr_df[gene_expr_df > 1].count() / len(gene_expr_df)
    gnames = genes_prop[genes_prop > expression_cutoff].index
    gene_expr_fpkm_filtered = gene_expr_df[gnames]

    return gene_expr_fpkm_filtered


def select_n_var_genes(gene_expr_df, n_var_genes=250):
    """ Select n most variable genes from the original datset and leaves only them """

    gene_names_most_var = gene_expr_df.var().sort_values(
        ascending=False)[:n_var_genes].index
    gene_expr_var_filtered = gene_expr_df.loc[:, gene_names_most_var]

    return gene_expr_var_filtered


def rank_transform(gene_expr, mode='linear', rank_method='average'):
    """
        Perform rank transformation: rank the genes, so that the highest expression
        would have the highest rank (making it the most important gene relative to others)

        Input: pandas dataframe, gene expression matrix; samples x features
        Output: pandas dataframe, rank-normalized gene expression matrix
    """
    if mode == 'linear':
        gene_expr_ranked = gene_expr.rank(axis=1, method=rank_method, pct=True)
    elif mode == 'log':
        # gene_expr_ranked = np.log2(gene_expr.rank(axis=1, method='min', pct=True))
        gene_expr_ranked = np.log2(gene_expr.rank(axis=1, method=rank_method, pct=True))
    else:
        # defaulting to linear mode
        gene_expr_ranked = gene_expr.rank(axis=1, method=rank_method, pct=True)

    # gene_expr_ranked = gene_expr_ranked.div(
    #     len(gene_expr_ranked.columns))  # scale for the total number of genes
    return gene_expr_ranked


def split_data(gene_expr_rt, purities_data, types_data):

    # join the cancer types columns for fair type-stratification
    gene_expr_t = gene_expr_rt.join(types_data)

    # do the split
    gene_expr_train_t, gene_expr_test_t, purities_train, purities_test = train_test_split(
        gene_expr_t,
        purities_data,
        test_size=0.2,
        stratify=gene_expr_t.type,  # stratify according to type
        random_state=0,
    )

    # drop the types
    gene_expr_train, gene_expr_test = gene_expr_train_t.drop(
        'type', axis=1), gene_expr_test_t.drop('type', axis=1)

    return gene_expr_train, gene_expr_test, purities_train, purities_test


def standartise_data(gene_expr_train, gene_expr_test):
    """
        Input: gene expression train-test split
        Returns: standartised gene expression train-test split
                 optional - the scaler model

        Standartise expression data / do Z-score transformation:
        remove the mean and scale to variance for each feature.
    """

    # fit the scaler
    scaler = StandardScaler()
    scaler.fit(gene_expr_train)

    # transform the data
    gene_expr_train_st_val = scaler.transform(gene_expr_train)
    gene_expr_test_st_val = scaler.transform(gene_expr_test)

    # rebuild the data frames
    gene_expr_train_st = pd.DataFrame(
        gene_expr_train_st_val, index=gene_expr_train.index.values, columns=gene_expr_train.columns.values)
    gene_expr_test_st = pd.DataFrame(
        gene_expr_test_st_val, index=gene_expr_test.index.values, columns=gene_expr_test.columns.values)

    return gene_expr_train_st, gene_expr_test_st, scaler
