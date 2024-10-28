from DataGatherAndClean.directorHandling import findDirector
from DataGatherAndClean.GraphQLQueries import get


class Data:
    """
    maintains all relevant data related to anime and stores them in one of a few lists. Offers functions to access and
    update these lists. Also offers a function to handle reattempting getting and saving director data.
    """
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
        """
        self.formatData.append(row)

    def appendRequery(self, animeId: int) -> None:
        """
        add anime to stack to be re-queried for director information alter
        :param animeId: anime ID to be requeried
        """
        self.directorRequery.append(animeId)

    def popRequery(self) -> iter:
        """
        pop from re-query stack and yield the pop
        :return: anime ID to be requeried
        """
        if len(self.directorRequery) > 0:
            yield self.directorRequery.pop()

    def insertDirector(self, animeId: int, directorId: int) -> None:
        """
        for an animeId already in Data.animeData, add the directorId
        :param animeId: anime_id
        :param directorId: director_id
        :return: None
        """
        for row in self.animeData:  # animeData is not sorted based on row[0]. Might be an optimization point depending
            if row[0] == animeId:   # on how often we are insertDirector-in -- then we can binary search instead here.
                row[6] = directorId
                break

    def reprocessDirector(self) -> None:
        """
        re-query all anime in Data.appendRequery, this time for 25 roles(max amount of results) instead of 6
        :return: None
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
        return list of rows, depending on what tableName is. to be used to create DataFrames (hence table)
        :param tableName: name of list of rows we want
        :return: list of rows
        """
        match tableName:
            case 'anime':
                return self.animeData
            case 'genre':
                return self.genreData
            case 'format':
                return self.formatData


def processAnime(animeQuery: dict, data: Data, dropped: bool = False) -> None:
    """
    main anime processing function: tries to find director, formats data from GraphQL query, appends to Data.animeData
    :param animeQuery: GraphQL json of anime search results
    :param data: Data class that is storing tables
    :param dropped: boolean of if the watchlist was 'DROPPED' or not
    :return:
    """

    directorId: int | None = findDirector(animeQuery)
    if dropped:
        score = 0  # even if we initially gave it a good score, if dropped then we don't like it
    else:
        score = animeQuery['score']
    row: list = [animeQuery['media']['id'],
                 animeQuery['media']['title']['english'] or animeQuery['media']['title']['romaji'] or None,
                 animeQuery['media']['format'] or None,
                 animeQuery['media']['seasonYear'] or None,
                 animeQuery['media']['meanScore'] or None,
                 directorId,
                 score]
    print(f'Adding {row[1]} to database.')
    if directorId is None:
        data.appendRequery(row[0])
    data.appendAnime(row)


def processGenre(animeQuery: dict, data: Data) -> None:
    """
    main genre processing function: creates row of genre data for anime in animeQuery. since this is categorical data we
    are implementing genres as dummy variables.
    :param animeQuery: GraphQL json of anime search results
    :param data: Data class that is storing tables
    """
    animesGenres: list = [0 * n for n in range(19)]
    animesGenres[0] = animeQuery['media']['id']
    genres: list = animeQuery['media']['genres']
    for iterate, g in enumerate(
            ['anime_id', 'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror',
             'Mahou_Shoujo', 'Mecha', 'Music', 'Mystery', 'Psychological', 'Romance', 'Slice of Life', 'Sports',
             'Supernatural', 'Thriller']):
        if g in genres:
            animesGenres[iterate] = 1
    data.appendGenre(animesGenres)


def processFormat(animeQuery: dict, data: Data) -> None:
    """
    main format processing function: creates row of format data for anime in animeQuery. since this is categorical data
    we are implementing format as dummy variables. however, an anime can only have one format, so this might be more
    than necessary.
    :param animeQuery: GraphQL JSON of anime search results
    :param data: Data class that is storing tables
    :return:
    """
    formats: list = ['anime_id', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC']
    row: list = [0 * n for n in range(8)]
    row[0] = animeQuery['media']['id']
    entryFormat: str = animeQuery['media']['format']
    row[formats.index(entryFormat)] = 1
    data.appendFormat(row)
