from DataGatherAndClean.director import findDirector
from DataGatherAndClean.graphqlqueries import get

BASE_URL: str = 'https://anilist.co'
QUERY_URL: str = 'https://graphql.anilist.co'


class Data:
    def __init__(self, username: str):
        self.username: str = username
        self.directorRequery: list = []
        self.animeData: list = []
        self.genreData: list = []
        self.formatData: list = []

    def appendAnime(self, row: list):
        self.animeData.append(row)

    def appendGenre(self, row: list):
        self.genreData.append(row)

    def appendFormat(self, row: list):
        self.formatData.append(row)

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
        #  find anime in data.animeData, replace "None" with directorID
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


def processAnime(dct, data, dropped: bool = False):
    entries: list = dct['entries']
    for e in entries:
        directorId = findDirector(e)
        if dropped:
            score = 0
        else:
            score = e['score']
        row: list = [e['media']['id'],
                       e['media']['title']['english'] or e['media']['title']['romaji'],
                       e['media']['format'] or None,
                       e['media']['seasonYear'] or None,
                       e['media']['episodes'] or None,
                       e['media']['meanScore'] or None,
                       directorId,
                       score]
        if directorId is None:
            data.appendRequery(row[0])
        data.appendAnime(row)
        data.reprocessDirector()


def processGenre(dct, data):
    entries = dct['entries']
    for e in entries:
        row = [0 * n for n in range(19)]
        row[0] = e['media']['id']
        genres = e['media']['genres']
        for iterate, g in enumerate(
                ['anime_id', 'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror',
                 'Mahou_Shoujo', 'Mecha', 'Music', 'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports',
                 'Supernatural', 'Thriller']):
            if g in genres:
                row[iterate] = 1
        data.appendGenre(row)


def processFormat(dct, data):
    entries = dct['entries']
    formats = ['anime_id', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']
    for e in entries:
        row = [0 * n for n in range(8)]
        row[0] = e['media']['id']
        entryFormat = e['media']['format']
        row[formats.index(entryFormat)] = 1
        data.appendFormat(row)
