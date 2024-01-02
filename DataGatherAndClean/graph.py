import requests
import time

from DataGatherAndClean.graphqlqueries import queryAnimeLists, queryAnimeDirector, queryDirectorsWorks, queryAnimeScore

BASE_URL: str = 'https://anilist.co'
QUERY_URL: str = 'https://graphql.anilist.co'


class Data:
    def __init__(self, username: str):
        self.username: str = username
        self.directorRequery: list = []
        self.animeData: list = []
        self.genreData: list = []

    def appendAnime(self, row: list):
        self.animeData.append(row)

    def appendGenre(self, row: list):
        self.genreData.append(row)

    def appendRequery(self, animeId: int):
        self.directorRequery.append(animeId)

    def popRequery(self) -> iter:
        if len(self.directorRequery) > 0:
            yield self.directorRequery.pop()

    def insertDirector(self, animeId: int, directorId: int):
        for row in self.animeData:
            if row[0] == animeId:
                row[6] = directorId
                break

    def reprocessDirector(self):
        #  go through requery queue (rate limit)
        #  query for director (bigger page size, only staff?)
        #  find anime in data.animeData, replace "n/a" with directorID
        for animeID in self.popRequery():
            if animeID is None:
                break
            result = get('AnimeDirector', animeID, True)
            entry = result['data']
            directorId = findDirector(entry)
            self.insertDirector(animeID, directorId)

    def returnTable(self, tableName: str) -> list:
        match tableName:
            case 'anime':
                return self.animeData
            case 'genre':
                return self.genreData


def rateLimitHit(JSONdict: dict) -> bool:
    """
    determines if we hit the rate limit
    :param JSONdict: dict deserialized from a json string
    :return: boolean of if we hit the rate limit
    """
    return JSONdict['data'] is None and JSONdict['errors'][0]['status'] == 429


def get(kind: str, queryVariable: str | int, rateLimit: bool = True) -> dict:
    """
    for an aniList username, query for all their watchlists
    :param kind: which query
    :param queryVariable: variables for the query
    :param rateLimit:
    :return: list of watchlists
    """
    response: requests.Response
    searchResults: dict
    animeLists: list
    query: str = ""
    varString: str = ""
    match kind:
        case 'AnimeLists':
            query = queryAnimeLists
            varString = 'username'
        case 'AnimeDirector':
            query = queryAnimeDirector
            varString = 'mediaId'
        case 'DirectorsWorks':
            query = queryDirectorsWorks
            varString = 'directorId'
        case 'AnimeScore':
            query = queryAnimeScore
            varString = 'mediaId'
    if rateLimit:
        time.sleep(2)
    response = requests.post(QUERY_URL, json={'query': query, 'variables': {varString: queryVariable}})
    searchResults = response.json()
    # print(searchResults)
    if rateLimitHit(searchResults):
        print('hit the rate limit, try again')
    return searchResults


def processAnime(dct, data, dropped: bool = False):
    entries: list = dct['entries']
    for e in entries:
        directorId: int = findDirector(e)
        if dropped:
            score = 0
        else:
            score = e['score']
        anime: list = [e['media']['id'],
                       e['media']['title']['english'] or e['media']['title']['romaji'],
                       e['media']['format'] or 'N/A',
                       e['media']['seasonYear'] or 'N/A',
                       e['media']['episodes'] or 'N/A',
                       e['media']['meanScore'] or 'N/A',
                       directorId,
                       score]
        if directorId == 'N/A':
            data.appendRequery(anime[0])
        data.appendAnime(anime)
        data.reprocessDirector()


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
    print(entry)
    try:
        for staff in entry['media']['staff']['edges']:
            if staff['role'] == 'Director':
                directorId = staff['node']['id']
                break
        return directorId
    except KeyError:
        for staff in entry['Media']['staff']['edges']:
            if staff['role'] == 'Director':
                directorId = staff['node']['id']
                break
        return directorId
