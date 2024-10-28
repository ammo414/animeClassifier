import pickle
import pandas as pd
from sklearn.ensemble import StackingClassifier
from flask import Flask, jsonify

from DataGatherAndClean.GraphQLQueries import get
from DataGatherAndClean.directorHandling import (
    findDirector,
    pullDirectorStatsFromDF,
    isDirectorInDF,
)
from DataTrainAndTest.loadDataFrames import loadFromCSV


def load_model(filename):
    """
    loads a model from a given .pickle file
    :param filename: file containing pickled model
    :return: model
    """
    with open(f"./PickleJar/{filename}.pickle", mode="rb") as pickle_model:
        model: StackingClassifier = pickle.load(pickle_model)
    return model


def preprocess_input(query: str, dir_DF: pd.DataFrame) -> tuple:
    """
    using the HTTP input, which should be an anime title, sends out a GraphQL query and gets all relevant data. then
    returns that data back to be sent to the model for prediction.
    :param query: anime title
    :return: list of anime Data, aniList's anime ID, title of anime (mainly for troubleshooting)
    """
    searchResults: dict
    if query.isnumeric():
        searchResults = get("NewAnimeID", query, False)
    else:
        searchResults = get("NewAnimeTitle", query, False)

    animeJSON: dict = searchResults["data"]
    requestDict: dict = processAnime(animeJSON)
    requestDict.update(processGenre(animeJSON))
    requestDict.update(processFormat(animeJSON))
    directorId: int | None
    directorId = requestDict.get("director_id", None)

    requestList: list = convertReqDictToReqList(requestDict, dir_DF, directorId)

    return requestList, requestDict["anime_id"], requestDict["title"]


def convertReqDictToReqList(
    requestDict: dict, dir_DF: pd.DataFrame, directorId: int | None = None
) -> list:
    """
    takes in a dict of the queried anime's data and converts it to a 2D list to send to the model
    :param requestDict: dict of queried anime's data
    :return: 2D array of queried anime's data
    """
    requestList: list = [
        requestDict["year_released"],
        requestDict["a_mean_score"],
        requestDict["Action"],
        requestDict["Adventure"],
        requestDict["Comedy"],
        requestDict["Drama"],
        requestDict["Ecchi"],
        requestDict["Sci-Fi"],
        requestDict["Fantasy"],
        requestDict["Horror"],
        requestDict["Mahou_Shoujo"],
        requestDict["Mecha"],
        requestDict["Music"],
        requestDict["Mystery"],
        requestDict["Psychological"],
        requestDict["Romance"],
        requestDict["Slice of Life"],
        requestDict["Sports"],
        requestDict["Supernatural"],
        requestDict["Thriller"],
        requestDict["TV"],
        requestDict["TV_SHORT"],
        requestDict["MOVIE"],
        requestDict["SPECIAL"],
        requestDict["OVA"],
        requestDict["ONA"],
        requestDict["MUSIC"],
    ]
    if directorId:
        if isDirectorInDF(directorId, dir_DF):
            directorStats = pullDirectorStatsFromDF(directorId, dir_DF)
            requestList += directorStats
    return [requestList]


def processAnime(animeJSON: dict) -> dict:
    """
    creates a dict of anime data from the GraphQL results
    :param animeJSON: GraphQL results
    :return: dict of anime data
    """
    animeDict: dict
    directorID: int | None = findDirector(animeJSON)
    animeJSON: dict = animeJSON["Media"]
    animeDict = {
        "anime_id": animeJSON["id"],
        "title": animeJSON["title"]["english"] or animeJSON["title"]["romaji"] or None,
        "format": animeJSON["format"],
        "year_released": animeJSON["startDate"]["year"],
        "a_mean_score": animeJSON["meanScore"],
        "director_id": directorID,
    }
    return animeDict


def processGenre(animeJSON: dict) -> dict:
    """
    creates a dict of genre data from the GraphQL query results
    :param animeJSON: GraphQL results
    :return: dict of genre data
    """
    genreDct: dict = {}
    genres: list = animeJSON["Media"]["genres"]
    for g in [
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
    ]:
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
    formatDct: dict = {
        "TV": 0,
        "TV_SHORT": 0,
        "MOVIE": 0,
        "SPECIAL": 0,
        "OVA": 0,
        "ONA": 0,
        "MUSIC": 0,
    }
    animesFormat: str = animeJSON["Media"]["format"]
    formatDct[animesFormat] = 1
    return formatDct

def mainCall():
    app: Flask = Flask(__name__)
    stackedDirModel: StackingClassifier = load_model("dirClassifier")
    stackedNoDirModel: StackingClassifier = load_model("noDirClassifier")
    directorDF: pd.DataFrame = loadFromCSV("directorDF").astype("float")

    @app.route("/api/<path:aniListURL>", methods=["GET"])
    def animeIDHandle(aniListURL: str) -> dict:
        URLParts = aniListURL.split("/")
        animeId: int
        for p in URLParts:
            if p.isnumeric():
                animeId = p
                break
        return servePrediction(animeId)
    
    @app.route("/api/<string:animeTitle>", methods=["GET"])
    def animeTitleHandle(animeTitle: str) -> dict:
        return servePrediction(animeTitle)

    def servePrediction(query: str) -> dict:
        processedQuery, animeId, matchedTitle = preprocess_input(query, directorDF)
        prediction: bool
        print(processedQuery)
        if len(processedQuery[0]) == 29:
            prediction = stackedDirModel.predict(processedQuery)[0]
        else:
            prediction = stackedNoDirModel.predict(processedQuery)[0]
        
        print(prediction)
        print(len(processedQuery[0]))

        retJSON: dict = {
            "prediction": prediction,
            "animeID": animeId,
            "matchedTitle": matchedTitle,
        }
        return jsonify(retJSON)

    app.run(debug=True, port=8414)

if __name__ == "__main__":
    mainCall()