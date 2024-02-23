import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression

from loadDataFrames import loadFromCSV, createFullDFRecursive


def fitModel(X, y):
    logRegDirector = LogisticRegression(random_state=16, max_iter=500)
    logRegDirector.fit(X, y)
    return logRegDirector


def trainModels(fullDataFrame):
    featureColumnsNoDirector = ['year_released', 'a_mean_score', 'Action', 'Adventure', 'Comedy', 'Drama',
                                'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror', 'Mahou_Shoujo', 'Mecha', 'Music',
                                'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports',
                                'Supernatural', 'Thriller', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']
    DirectorFeatureColumns = ['d_mean_score', 'd_do_I_like']
    featureColumnsAll = featureColumnsNoDirector + DirectorFeatureColumns
    director = fitModel(X=fullDataFrame[featureColumnsAll],
                        y=fullDataFrame['a_do_I_like'])
    noDirector = fitModel(X=fullDataFrame[featureColumnsNoDirector], y=fullDataFrame['a_do_I_like'])

    return director, noDirector


def mainTrainModel():
    allCSVs = ['animeDF', 'formatDF', 'genreDF', 'directorDF']
    animeDF = loadFromCSV('animeDF')
    formatDF = loadFromCSV('formatDF')
    genreDF = loadFromCSV('genreDF')
    directorDF = loadFromCSV('directorDF')
    joiningDataFrames = [formatDF, genreDF, directorDF]
    mergePoints = ['anime_id', 'anime_id', 'director_id']
    fullDF: pd.DataFrame = pd.DataFrame()
    fullDF = createFullDFRecursive(animeDF, joiningDataFrames, mergePoints)
    # to csv just for fun
    fullDF.to_csv('~/PycharmProjects/animeClassifier/fullDF.csv', index=False)

    directorModel, noDirectorModel = trainModels(fullDF)

    pickle.dump(directorModel, open('/home/anmol/PycharmProjects/animeClassifier/directorModel.pickle', mode="wb"))
    pickle.dump(noDirectorModel, open('/home/anmol/PycharmProjects/animeClassifier/noDirectorModel.pickle', mode="wb"))


if __name__ == '__main__':
    mainTrainModel()


