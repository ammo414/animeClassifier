import pickle
from sklearn.linear_model import LogisticRegression
from flask import request, jsonify, Flask

from DataGatherAndClean.GraphQLQueries import get
from DataGatherAndClean.directorHandling import findDirector


def load_model(filename):
    """
    loads a model from a given .pickle file
    :param filename: file containing pickled model
    :return: LogisticRegression model
    """
    with open(f'/home/anmol/PycharmProjects/animeClassifier/{filename}.pickle', mode='rb') as pickle_model:
        model = pickle.load(pickle_model)
    return model


def preprocess_input(query: str) -> tuple:
    """
    using the HTTP input, which should be an anime title, sends out a GraphQL query and gets all relevant data. then
    returns that data back to be sent to the model for prediction.
    :param query: anime title
    :return: list of anime Data, aniList's anime ID, title of anime (mainly for troubleshooting)
    """
    searchResults: dict = get('NewAnime', query, True)

    animeJSON: dict = searchResults['data']
    requestDict: dict = processAnime(animeJSON)
    requestDict.update(processGenre(animeJSON))
    requestDict.update(processFormat(animeJSON))

    return convertreqDictToReqList(requestDict), requestDict['anime_id'], requestDict['title']


def convertreqDictToReqList(requestDct: dict) -> list:
    """
    takes in a dict of the queried anime's data and converts it to a 2D list to send to the model
    :param requestDct: dict of queried anime's data
    :return: 2D array of queried anime's data
    """
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
    return [requestList]


def processAnime(animeJSON: dict) -> dict:
    """
    creates a dict of anime data from the GraphQL results
    :param animeJSON: GraphQL results
    :return: dict of anime data
    """
    animeDct: dict = {}
    directorID: int | None = findDirector(animeDct)
    animeJSON: dict = animeDct['Media']
    animeDct = {'anime_id': animeJSON['id'],
                'title': animeJSON['title']['english'] or animeJSON['title']['romanji'] or None,
                'format': animeJSON['format'],
                'year_released': animeJSON['startDate']['year'],
                'a_mean_score': animeJSON['meanScore'],
                'director_id': directorID}
    return animeDct


def processGenre(animeJSON: dict) -> dict:
    """
    creates a dict of genre data from the GraphQL query results
    :param animeJSON: GraphQL results
    :return: dict of genre data
    """
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


def processFormat(animeJSON: dict) -> dict:
    """
    creates a dict of format data from the GraphQL query results
    :param animeJSON: GraphQL results
    :return: dict of format data
    """
    formatDct: dict = {'TV': 0, 'TV_SHORT': 0, 'MOVIE': 0, 'SPECIAL': 0, 'OVA': 0, 'ONA': 0, 'MUSIC': 0}
    animesFormat: str = animeJSON['Media']['format']
    formatDct[animesFormat] = 1
    return formatDct


def predict(model: LogisticRegression, query: list) -> list:
    prediction = model.predict(query)
    return prediction


if __name__ == '__main__':
    app = Flask(__name__)
    logModel_noDirector = load_model('noDirector')


    @app.route('/api/<string:animeTitle>', methods=['GET'])
    def servePrediction(animeTitle: str) -> dict:

        processedQuery, animeId, matchedTitle = preprocess_input(animeTitle)
        pred: list = predict(logModel_noDirector, processedQuery)
        print(pred)

        '''try:
            animeTitle = request.args.get('title', '')

            processedQuery = preprocess_input(animeTitle)
            pred = predict(logModel_noDirector, processedQuery)
        except Exception as e:
            print(f'{e} occurred while processing anime')
            return str(e), 500'''
        retJSON: dict= {'prediction': pred[0],
                        'animeId': animeId,
                        'matchedTitle': matchedTitle}
        return jsonify(retJSON)


    app.run(debug=True, port=8080)
