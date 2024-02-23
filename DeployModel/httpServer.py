import pickle
from sklearn.linear_model import LogisticRegression
from flask import request, jsonify, Flask
from DataGatherAndClean.graphqlqueries import get
from DataGatherAndClean.director import findDirector


def load_model():
    with open('/home/anmol/PycharmProjects/animeClassifier/noDirectorModel.pickle', mode='rb') as pickle_model:
        model = pickle.load(pickle_model)
    return model


def preprocess_input(animeTitle):
    print(f'Looking up recs for {animeTitle}')
    searchResults = get('NewAnime', animeTitle, True)
    return unpackRequest(searchResults)


def convertreqDictToReqList(requestDct):
    requestList: list = [requestDct['year_released'],
                         requestDct['a_mean_score'],
                         requestDct['Action'],
                         requestDct['Adventure'],
                         requestDct['Comedy'],
                         requestDct['Drama'],
                         requestDct['Ecchi'],
                         requestDct['Sci-Fi'],
                         requestDct['Fantasy'],
                         requestDct['Horror'],
                         requestDct['Mahou_Shoujo'],
                         requestDct['Mecha'],
                         requestDct['Music'],
                         requestDct['Mystery'],
                         requestDct['Psychological'],
                         requestDct['Romance'],
                         requestDct['Slice of Life'],
                         requestDct['Sports'],
                         requestDct['Supernatural'],
                         requestDct['Thriller'],
                         requestDct['TV'],
                         requestDct['TV_SHORT'],
                         requestDct['MOVIE'],
                         requestDct['SPECIAL'],
                         requestDct['OVA'],
                         requestDct['ONA'],
                         requestDct['MUSIC']]
    print(requestList)
    return requestList


def unpackRequest(searchResults):
    animeJSON: dict = searchResults['data']
    requestDict: dict = processAnime(animeJSON)
    requestDict.update(processGenre(animeJSON))
    requestDict.update(processFormat(animeJSON))

    return [convertreqDictToReqList(requestDict)] # have to make it 2D


def processAnime(animeJSON):
    animeDct: dict = {}
    directorID = findDirector(animeJSON)
    animeJSON = animeJSON['Media']
    animeDct = {'anime_id': animeJSON['id'],
                'title': animeJSON['title']['english'] or animeJSON['title']['romanji'] or None,
                'format': animeJSON['format'],
                'year_released': animeJSON['startDate']['year'],
                'a_mean_score': animeJSON['meanScore'],
                'director_id': directorID}
    return animeDct


def processGenre(animeJSON):
    genreDct: dict = {}
    genres: list = animeJSON['Media']['genres']
    for g in ['Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror',
              'Mahou_Shoujo', 'Mecha', 'Music', 'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports',
              'Supernatural', 'Thriller']:
        if g in genres:
            genreDct[g] = 1
        else:
            genreDct[g] = 0
    return genreDct


def processFormat(animeJSON):
    formatDct: dict = {'TV': 0, 'TV_SHORT': 0, 'MOVIE': 0, 'SPECIAL': 0, 'OVA': 0, 'ONA': 0, 'MUSIC': 0}
    animesFormat: str = animeJSON['Media']['format']
    formatDct[animesFormat] = 1
    return formatDct


def predict(model: LogisticRegression, query):
    prediction = model.predict(query)
    return prediction


if __name__ == '__main__':
    app = Flask(__name__)
    logModel_noDirector = load_model()


    @app.route('/api/<string:query>', methods=['GET'])
    def servePrediction(query):
        animeTitle = query

        processedQuery = preprocess_input(animeTitle)
        pred = predict(logModel_noDirector, processedQuery)
        print(pred)
        print(type(pred))
        '''try:
            animeTitle = request.args.get('title', '')

            processedQuery = preprocess_input(animeTitle)
            pred = predict(logModel_noDirector, processedQuery)
        except Exception as e:
            print(f'{e} occurred while processing anime')
            return str(e), 500'''
        return pred[0]


    app.run(debug=True, port=8080)
