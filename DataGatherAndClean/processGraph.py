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


def processAnime(animeData: dict, data: Data, dropped: bool = False) -> None:
    """
    main anime processing function
    :param animeData: graphql json of anime search results
    :param data: Data class storing tables
    :param dropped: flag of if the watchlist was 'DROPPED' or not
    :return:
    """

    directorId: int | None = findDirector(animeData)
    if dropped:
        score = 0  # even if we initially gave it a good score, if dropped then we don't like it
    else:
        score = animeData['score']
    row: list = [animeData['media']['id'],
                 animeData['media']['title']['english'] or animeData['media']['title']['romaji'] or None,
                 animeData['media']['format'] or None,
                 animeData['media']['seasonYear'] or None,
                 animeData['media']['meanScore'] or None,
                 directorId,
                 score]
    print(f'Adding {row[1]} to database')
    if directorId is None:
        data.appendRequery(row[0])
    data.appendAnime(row)


def processGenre(animeData: dict, data: Data) -> None:
    """
    main genre processing function. creates DataFrame of genre data for each anime
    :param animeData:
    :param data:
    """
    animesGenres: list = [0 * n for n in range(19)]
    animesGenres[0] = animeData['media']['id']
    genres: list = animeData['media']['genres']
    for iterate, g in enumerate(
            ['anime_id', 'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror',
             'Mahou_Shoujo', 'Mecha', 'Music', 'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports',
             'Supernatural', 'Thriller']):
        if g in genres:
            animesGenres[iterate] = 1
    data.appendGenre(animesGenres)


def processFormat(animeData: dict, data: Data) -> None:
    formats: list = ['anime_id', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']
    row: list = [0 * n for n in range(8)]
    row[0] = animeData['media']['id']
    entryFormat: str = animeData['media']['format']
    row[formats.index(entryFormat)] = 1
    data.appendFormat(row)

