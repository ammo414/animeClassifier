"""
maintains all relevant data related to anime and stores them in one of a few lists. Offers functions to access and
update these lists. Also offers a function to handle reattempting getting and saving director data.
"""

from DataGatherAndClean.GraphQLQueries import get
from DataGatherAndClean.directorHandling import findDirector

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