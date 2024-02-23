import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression

from loadDataFrames import loadFromCSV, createFullDF


animeDF: pd.DataFrame = loadFromCSV('animeDF')
formatDF: pd.DataFrame = loadFromCSV('formatDF')
genreDF: pd.DataFrame = loadFromCSV('genreDF')

DataFrames = [formatDF, genreDF]
mergePoints = ['anime_id', 'anime_id']
fullDF_NoDirector = createFullDF(animeDF, DataFrames, mergePoints)
fullDF_NoDirector.to_csv('~/PycharmProjects/animeClassifier/fullDF_NoDirector.csv', index=False)

featureColumns = ['year_released', 'episodes', 'a_mean_score', 'Action', 'Adventure', 'Comedy', 'Drama',
                  'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror', 'Mahou_Shoujo', 'Mecha', 'Music',
                  'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports', 'Supernatural',
                  'Thriller', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']
X = fullDF_NoDirector[featureColumns]
y = fullDF_NoDirector['a_do_I_like']

'''the below is training code, which is no longer needed

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=16)
logregNoDirector: LogisticRegression = LogisticRegression(random_state=16, max_iter=500)
logregNoDirector.fit(X_train, y_train)'''

logregNoDirector: LogisticRegression = LogisticRegression(random_state=16, max_iter=500)
logregNoDirector.fit(X, y)

pickle.dump(logregNoDirector, open('NoDirectorModel.pickle'))
