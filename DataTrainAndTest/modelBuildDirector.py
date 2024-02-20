import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from loadDataFrames import loadFromCSV, createFullDF


animeDF: pd.DataFrame = loadFromCSV('animeDF')
formatDF: pd.DataFrame = loadFromCSV('formatDF')
genreDF: pd.DataFrame = loadFromCSV('genreDF')
directorDF: pd.DataFrame = loadFromCSV('directorDF')

DataFrames = [formatDF, genreDF, directorDF]
mergePoints = ['anime_id', 'anime_id', 'director_id']
fullDF = createFullDF(animeDF, DataFrames, mergePoints)
fullDF.to_csv('~/PycharmProjects/animeClassifier/fullDF_Director.csv', index=False)

featureColumns = ['year_released', 'episodes', 'a_mean_score', 'd_mean_score', 'd_do_I_like', 'is_Action',
                  'is_Adventure', 'is_Comedy', 'is_Drama', 'is_Ecchi', 'is_Sci-Fi', 'is_Fantasy', 'is_Horror',
                  'is_Mahou_Shoujo', 'is_Mecha', 'is_Music', 'is_Mystery', 'is_Psychological', 'is_Romance',
                  'is_Slice of Life', 'is_Sports', 'is_Supernatural', 'is_Thriller', 'TV', 'TV_SHORT', 'MOVIE',
                  'SPECIAL', 'OVA', 'ONA', 'MUSIC']
X = fullDF[featureColumns]
y = fullDF['a_do_I_like']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=16)
logregDirector = LogisticRegression(random_state=16, max_iter=500)
logregDirector.fit(X_train, y_train)

pickle.dump(logregDirector, open('DirectorModel.pickle'))
y_prediction = logregDirector.predict(X_test)
