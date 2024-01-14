import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

animeDF: pd.DataFrame = pd.read_csv('~/PycharmProjects/animeClassifier/animeDF.csv', header=None)
animeDF.columns = animeDF.iloc[0]
animeDF = animeDF[1:]

directorDF: pd.DataFrame = pd.read_csv('~/PycharmProjects/animeClassifier/directorDF.csv', header=None)
directorDF.columns = directorDF.iloc[0]
directorDF = directorDF[1:]

formatDF: pd.DataFrame = pd.read_csv('~/PycharmProjects/animeClassifier/formatDF.csv', header=None)
formatDF.columns = formatDF.iloc[0]
formatDF = formatDF[1:]

genreDF: pd.DataFrame = pd.read_csv('~/PycharmProjects/animeClassifier/genreDF.csv', header=None)
genreDF.columns = genreDF.iloc[0]
genreDF = genreDF[1:]

fullDF: pd.DataFrame = pd.merge(animeDF, directorDF, how='inner', on='director_id')
fullDF = pd.merge(fullDF, genreDF, how='inner', on='anime_id')
fullDF = pd.merge(fullDF, formatDF, how='inner', on='anime_id')
fullDF.dropna(inplace=True)
fullDF.to_csv('~/PycharmProjects/animeClassifier/fullDF.csv', index=False)

featureColumns = ['year_released', 'episodes', 'a_mean_score', 'd_mean_score', 'd_do_I_like', 'is_Action',
                  'is_Adventure', 'is_Comedy', 'is_Drama', 'is_Ecchi', 'is_Sci-Fi', 'is_Fantasy', 'is_Horror',
                  'is_Mahou_Shoujo', 'is_Mecha', 'is_Music', 'is_Mystery', 'is_Psychological', 'is_Romance',
                  'is_Slice of Life', 'is_Sports', 'is_Supernatural', 'is_Thriller', 'TV', 'TV_SHORT', 'MOVIE',
                  'SPECIAL', 'OVA', 'ONA', 'MUSIC']
X = fullDF[featureColumns]
y = fullDF['a_do_I_like']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=16)
logreg = LogisticRegression(random_state=16)
logreg.fit(X_train, y_train)

y_prediction = logreg.predict(X_test)

print(X_train)
