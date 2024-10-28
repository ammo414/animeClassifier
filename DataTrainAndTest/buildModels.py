from pathlib import Path

import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.model_selection import train_test_split

from DataTrainAndTest.loadDataFrames import createFullDF


def trainModels(fullDataFrame: pd.DataFrame) -> tuple:
    """
    sets up features for all models and then fits them
    :param fullDataFrame: DataFrame with all the relevant data
    :return: both the directorModel and noDirectorModel
    """
    featureColumnsNoDirector = [
        "year_released",
        "a_mean_score",
        "Action",
        "Adventure",
        "Comedy",
        "Drama",
        "Ecchi",
        "Sci-Fi",
        "Fantasy",
        "Horror",
        "Mahou_Shoujo",
        "Mecha",
        "Music",
        "Mystery",
        "Psychological",
        "Romance",
        "Slice of Life",
        "Sports",
        "Supernatural",
        "Thriller",
        "TV",
        "TV_SHORT",
        "MOVIE",
        "SPECIAL",
        "OVA",
        "ONA",
        "MUSIC"
    ]
    featureColumnsDirector = ["d_mean_score", "d_do_I_like"]
    # Train two models, one without director data. 
    # Sometimes, director data isn't available for the prediction  
    allFeatureColumns = featureColumnsNoDirector + featureColumnsDirector

    XDir = fullDataFrame[allFeatureColumns]
    XNoDir = fullDataFrame[featureColumnsNoDirector]

    y = fullDataFrame["a_do_I_like"]

    classifiers = []
    for ds in [(XDir,y), (XNoDir,y)]:
        models = [
            ("lc", LogisticRegression(max_iter=10000)),
            ("rf", RandomForestClassifier()),
        ]
        stackedModel = StackingClassifier(models)
        X_train, _, y_train, _ = train_test_split(ds[0], ds[1], stratify=ds[1])
        classifiers.append(stackedModel.fit(X_train, y_train))

    return classifiers[0], classifiers[1]


def mainTrainModels() -> None:
    """
    loads DataFrames from .CSVs, creates a complete DataFrame,
    trains the models, and pickles the models for later use
    :return: None
    """

    fullDF = createFullDF()

    # to csv just for fun
    fullDF.to_csv("./data/fullDF.csv", index=False)

    stackedDir, stackedNoDir = trainModels(fullDF)
    dirFilePath = Path("./PickleJar/dirClassifier.pickle")
    noDirFilePath = Path("./PickleJar/noDirClassifier.pickle")
    pickleJar = Path("./PickleJar")

    if not pickleJar.is_dir():
        pickleJar.mkdir(parents=True)

    with dirFilePath.open(mode="wb") as file:
        pickle.dump(stackedDir, file)

    with noDirFilePath.open(mode="wb") as file:
        pickle.dump(stackedNoDir, file)

if __name__ == "__main__":
    mainTrainModels()
