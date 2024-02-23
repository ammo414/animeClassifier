import pandas as pd


def loadFromCSV(filename: str) -> pd.DataFrame:
    """
    load DataFrame from .csv and handle columns
    :param filename: filename of .csv
    :return: DataFrame
    """
    df: pd.DataFrame = pd.read_csv(f'~/PycharmProjects/animeClassifier/{filename}.csv', header=None)
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def createFullDFRecursive(baseDF: pd.DataFrame, joins: list, mergePoints: list) -> pd.DataFrame:
    """
    inner joins/merges a bunch of DataFrames and drops any rows with None values. does so recursively because it is a
    bit more intuitive, but should be identical in functionality to createFullDF
    :param baseDF: starting DF. since these are inner joins rather than left joins, order shouldn't matter.
    :param joins: list of the rest of the DataFrames
    :param mergePoints: list of the columns that we are joining/merging on
    :return:
    """
    if len(joins) == 0:
        return baseDF.dropna()
    else:
        fullDF = pd.merge(baseDF, joins[0], how='inner', on=mergePoints[0])
        return createFullDFRecursive(fullDF, joins[1:], mergePoints[1:])


def createFullDF(baseDF: pd.DataFrame, joins: list, mergePoints: list) -> pd.DataFrame:
    """
    inner joins/merges a bunch of DataFrames and drops any rows with None values. should be identical in functionality
    to createFullDFRecursive
    :param baseDF: starting DF. since these are inner joins rather than left joins, order shouldn't matter.
    :param joins: list of the rest of the DataFrames
    :param mergePoints:
    :return:
    """
    for iterator, df in enumerate(joins):
        fullDF = pd.merge(fullDF, df, how='inner', on=mergePoints[iterator])
    return fullDF.dropna()
