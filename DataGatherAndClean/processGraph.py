from DataGatherAndClean.director import findDirector
from DataGatherAndClean.graphqlqueries import get


class Data:
    def __init__(self, username: str):
        self.username: str = username
        self.directorRequery: list = []
        self.animeData: list = []
        self.genreData: list = []
        self.formatData: list = []

    def appendAnime(self, row: list) -> None:
        """
        add row to Data.animeData
        :param row: row of data
        """
        self.animeData.append(row)

    def appendGenre(self, row: list) -> None:
        """
        add row to Data.genreData
        :param row: row of data
        """
        self.genreData.append(row)

    def appendFormat(self, row: list) -> None:
        """
        add row to Data.formatData
        :param row: row of data
        :return:
        """
        self.formatData.append(row)

    def appendRequery(self, animeId: int) -> None:
        """
        add anime to stack to be re-queried for director information alter
        :param animeId:
        """
        self.directorRequery.append(animeId)

    def popRequery(self) -> iter:
        """
        pop from re-query stack and yield the pop
        :return: animeId to be re-queried
        """
        if len(self.directorRequery) > 0:
            yield self.directorRequery.pop()

    def insertDirector(self, animeId: int, directorId: int) -> None:
        """
        for an animeId already in Data.animeData, add the directorId
        :param animeId: anime_id
        :param directorId: director_id
        :return:
        """
        for row in self.animeData:
            if row[0] == animeId:
                row[6] = directorId
                break

    def reprocessDirector(self):
        """
        re-query all anime in Data.appendRequery, this time for 25 roles instead of 6
        :return:
        """
        for animeID in self.popRequery():
            if animeID is None:
                break
            result = get('AnimeDirector', animeID, True)
            entry = result['data']
            directorId = findDirector(entry)
            self.insertDirector(animeID, directorId)

    def returnTable(self, tableName: str) -> list:
        """
        return list of rows, depending on what tableName is
        :param tableName: name of table we want
        :return:
        """
        match tableName:
            case 'anime':
                return self.animeData
            case 'genre':
                return self.genreData
            case 'format':
                return self.formatData


def processAnime(json: dict, data: Data, dropped: bool = False) -> None:
    """
    main anime processing function
    :param json: graphql json of anime search results
    :param data: Data class storing tables
    :param dropped: flag of if the watchlist was 'DROPPED' or not
    :return:
    """
    entries: list = json['entries']
    for e in entries:
        directorId: int | None = findDirector(e)
        if dropped:
            score = 0  # even if we gave it a good score, we want to say we don't like it
        else:
            score = e['score']
        row: list = [e['media']['id'],
                       e['media']['title']['english'] or e['media']['title']['romaji'] or None,
                       e['media']['format'] or None,
                       e['media']['seasonYear'] or None,
                       e['media']['meanScore'] or None,
                       directorId,
                       score]
        print(f'Adding {row[1]} to database')
        if directorId is None:
            data.appendRequery(row[0])
        data.appendAnime(row)


def processGenre(json: dict, data: Data) -> None:
    entries: list = json['entries']
    for e in entries:
        row: list = [0 * n for n in range(19)]
        row[0] = e['media']['id']
        genres: list = e['media']['genres']
        for iterate, g in enumerate(
                ['anime_id', 'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror',
                 'Mahou_Shoujo', 'Mecha', 'Music', 'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports',
                 'Supernatural', 'Thriller']):
            if g in genres:
                row[iterate] = 1
        data.appendGenre(row)


def processFormat(json: dict, data: Data) -> None:
    entries: list = json['entries']
    formats: list = ['anime_id', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']
    for e in entries:
        row: list = [0 * n for n in range(8)]
        row[0] = e['media']['id']
        entryFormat: str = e['media']['format']
        row[formats.index(entryFormat)] = 1
        data.appendFormat(row)
