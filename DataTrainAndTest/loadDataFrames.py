import pandas as pd


def loadFromCSV(filename: str) -> pd.DataFrame:
    """
    load DataFrame from .csv and handle columns
    :param filename: filename of .csv (not filepath)
    :return: DataFrame
    """
    df: pd.DataFrame = pd.read_csv(f"./data/{filename}.csv", header=None)
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def createFullDF():
    allJoiningCSVs = ["formatDF", "genreDF", "directorDF"]
    animeDF = loadFromCSV("animeDF")
    formatDF = loadFromCSV("formatDF")
    genreDF = loadFromCSV("genreDF")
    directorDF = loadFromCSV("directorDF")
    joiningDataFrames = [formatDF, genreDF, directorDF]
    joiningDataFrames = [loadFromCSV(csv) for csv in allJoiningCSVs]
    mergePoints = ["anime_id", "anime_id", "director_id"]  # columns to "join" on
    return joinDF(animeDF, joiningDataFrames, mergePoints)


def joinDF(
    baseDF: pd.DataFrame, joins: list, mergePoints: list
) -> pd.DataFrame:
    """
    inner joins/merges a bunch of DataFrames and drops any rows with None values.
    :param baseDF: starting DF. since these are inner joins rather than left joins, order shouldn't matter.
    :param joins: list of the rest of the DataFrames
    :param mergePoints: list of the columns that we are joining/merging on
    :return:
    """
    if len(joins) == 0:
        return baseDF.dropna()
    
    fullDF = pd.merge(baseDF, joins[0], how="inner", on=mergePoints[0])
    return joinDF(fullDF, joins[1:], mergePoints[1:])
