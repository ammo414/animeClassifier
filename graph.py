import pandas as pd
import requests
import time

from graphqlqueries import queryAnimeLists, queryAnimeDirectorDetails, queryDirectorsWork

BASE_URL: str = 'https://anilist.co'
QUERY_URL: str = 'https://graphql.anilist.co'


class Data:
    def __init__(self, name):
        self.username: str = name
        self.directorRequery: list = []
        self.animeData: list = []
        self.genreData: list = []
        self.directorData: list = []
        self.animeData.append(['anime_id', 'title', 'format', 'year_released', 'episodes', 'mean_score', 'director_id',
                               'score'])
        self.genreData.append(['anime_id', 'is_Action', 'is_Adventure', 'is_Comedy', 'is_Drama', 'is_Ecchi',
                               'is_Sci-Fi', 'is_Fantasy', 'is_Horror', 'is_Mahou_Shoujo', 'is_Mecha', 'is_Music',
                               'is_Mystery', 'is_Psychological', 'is_Romance', 'is_Slice of Life', 'is_Sports',
                               'is_Supernatural', 'is_Thriller'])
        self.directorData.append(['director_id', 'name', 'isPopular', 'doILike'])
        self.df: pd.DataFrame = pd.DataFrame()  # for the sake of typing, this has to be done

    def appendAnime(self, row):
        self.animeData.append(row)

    def appendGenre(self, row):
        self.genreData.append(row)

    def appendDirector(self, row):
        self.directorData.append(row)

    def queueRequery(self, animeId: int, page: int):
        self.directorRequery.append((animeId, page))

    def popRequery(self):
        yield self.directorRequery.pop()

    def insertDirector(self, animeId, directorId):
        for row in self.animeData:
            if row[0] == animeId:
                row[6] = directorId

    def selectDirectorIDFromAnime(self):
        return [row[6] for row in self.animeData]


def rateLimitHit(JSONdict: dict) -> bool:
    """
    determines if we hit the rate limit
    :param JSONdict: dict deserialized from a json string
    :return: boolean of if we hit the rate limit
    """
    return JSONdict['data'] is None and JSONdict['errors'][0]['status'] == 429


def getAnimeLists(username: str) -> list:
    """
    for an aniList username, query for all their watchlists
    :param username: aniList username
    :return: list of watchlists
    """
    query: str
    response: requests.Response
    searchResults: dict
    animeLists: list

    query = queryAnimeLists
    response = requests.post(QUERY_URL, json={'query': query, 'variables': {'username': username}})
    searchResults = response.json()
    # print(searchResults)
    if rateLimitHit(searchResults):
        print('hit the rate limit, try again')
    animeLists = searchResults['data']['MediaListCollection']['lists']
    return animeLists


def get(kind: str, queryVariable: str) -> list:
    """
    for an aniList username, query for all their watchlists
    :param username: aniList username
    :return: list of watchlists
    """
    query: str
    response: requests.Response
    searchResults: dict
    animeLists: list
    varString: str
    match kind:
        case 'AnimeLists':
            query = queryAnimeLists
            varString = 'username'
        case 'AnimeDirector':
            query = queryAnimeDirectorDetails
            varString = 'mediaId'
        case 'DirectorsWorks':
            query = queryDirectorsWork
            varString = 'directorId'
    response = requests.post(QUERY_URL, json={'query': query, 'variables': {varString: queryVariable}})
    searchResults = response.json()
    # print(searchResults)
    if rateLimitHit(searchResults):
        print('hit the rate limit, try again')
    return searchResults


def processAnime(dct, data):
    entries = dct['entries']  # lst[0] = dct['']
    for e in entries:
        directorId = findDirector(e)
        anime: list = [e['media']['id'],
                       e['media']['title']['english'] or e['media']['title']['romaji'],
                       e['media']['format'] or 'N/A',
                       e['media']['seasonYear'] or 'N/A',
                       e['media']['episodes'] or 'N/A',
                       e['media']['meanScore'] or 'N/A',
                       directorId,
                       e['score']]
        # print(anime)
        if directorId == 'N/A':
            data.queueRequery(anime[0], 1)
        data.appendAnime(anime)


def processGenre(dct, data):
    entries = dct['entries']
    for e in entries:
        lst = [0 + n for n in range(19)]
        animeId = e['media']['id']
        lst[0] = animeId
        genres = e['media']['genres']
        for iterate, g in enumerate(
                ['anime_id', 'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror',
                 'Mahou_Shoujo', 'Mecha', 'Music', 'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports',
                 'Supernatural', 'Thriller']):
            if g in genres:
                lst[iterate] = 1
        data.appendGenre(lst)


def findDirector(entry):
    directorId = 'N/A'
    for staff in entry['media']['staff']['edges']:
        if staff['role'] == 'Director':
            directorId = staff['id']
            break
    return directorId


def processDirector(dct, data):
    #  go through requery queue (rate limit)
    #  query for director (bigger page size, only staff?)
    #  find anime in data.animeData, replace "n/a" with directorID
    for animeID in data.popRequery():
        time.sleep(2)
        result = get('AnimeDirector', animeID)
        entry = result['data']
        directorId = findDirector(entry)
        data.insertDirector(animeID, directorId)
    #  get director's anime
    #  get average score of all anime
    #  get my score of anime, if relevant
    directorIds = data.selectDirectorIDFromAnime()
    for dID in directorIds:
        time.sleep(2)
        searchResults = get('DirectorsWorks', dID)


def main():
    d = Data('wannabe414')
    results = get('AnimeLists', 'wannabe414')
    lst = results['data']['MediaListCollection']['lists']
    for x in lst:
        if x['status'] == "COMPLETED":
            processAnime(x, d)
            processGenre(x, d)
        # print(x)
    # print(d.animeData)
    print(d.genreData)


main()
