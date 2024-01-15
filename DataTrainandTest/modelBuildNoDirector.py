import pandas as pd
import sklearn.linear_model
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle

from loadDataFrames import loadFromCSV, createFullDF


animeDF: pd.DataFrame = loadFromCSV('animeDF')
formatDF: pd.DataFrame = loadFromCSV('formatDF')
genreDF: pd.DataFrame = loadFromCSV('genreDF')

DataFrames = [formatDF, genreDF]
mergePoints = ['anime_id', 'anime_id']
fullDF = createFullDF(animeDF, DataFrames, mergePoints)
fullDF.to_csv('~/PycharmProjects/animeClassifier/fullDF_NoDirector.csv', index=False)

featureColumns = ['year_released', 'episodes', 'a_mean_score', 'is_Action', 'is_Adventure', 'is_Comedy', 'is_Drama',
                  'is_Ecchi', 'is_Sci-Fi', 'is_Fantasy', 'is_Horror', 'is_Mahou_Shoujo', 'is_Mecha', 'is_Music',
                  'is_Mystery', 'is_Psychological', 'is_Romance', 'is_Slice of Life', 'is_Sports', 'is_Supernatural',
                  'is_Thriller', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']
X = fullDF[featureColumns]
y = fullDF['a_do_I_like']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=16)
logregNoDirector: sklearn.linear_model.LogisticRegression = LogisticRegression(random_state=16, max_iter=500)
logregNoDirector.fit(X_train, y_train)

pickle.dump(logregNoDirector, open('directorModel.pickle'))
y_prediction = logregNoDirector.predict(X_test)
