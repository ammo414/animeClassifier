import pandas as pd


def loadFromCSV(dfName: str) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_csv(f'~/PycharmProjects/animeClassifier/{dfName}.csv')
    return df


def createFullDFRecursive(fullDF: pd.DataFrame, DataFrames: list, mergePoints: list) -> pd.DataFrame:
    if len(DataFrames) == 0:
        return fullDF
    else:
        fullDF = pd.merge(fullDF, DataFrames[0], how='inner', on=mergePoints[0])
        return createFullDFRecursive(fullDF, DataFrames[1:], mergePoints[1:]).dropna()


def createFullDF(baseDF: pd.DataFrame, joins: list, mergePoints: list) -> pd.DataFrame:
    fullDF: pd.DataFrame = baseDF
    for iterator, df in enumerate(joins):
        fullDF = pd.merge(fullDF, df, how='inner', on=mergePoints[iterator])
    return fullDF.dropna()
