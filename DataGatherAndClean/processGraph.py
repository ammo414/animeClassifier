import pandas as pd

from DataGatherAndClean.directorHandling import findDirector
from DataGatherAndClean.GraphQLQueries import get
from DataGatherAndClean.animeData import Data


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

def getAllData(username: str) -> Data:
    userData = Data(username)
    results: dict = get('AnimeLists', username, False)
    listOfLists: list = results['data']['MediaListCollection']['lists']
    dropped: bool
    for animeList in listOfLists:
        if animeList['status'] == 'PLANNING':
            continue
        dropped = animeList['status'] == 'DROPPED'
        for anime in animeList['entries']:
            processAnime(anime, userData, dropped)
            processGenre(anime, userData)
            processFormat(anime, userData)
    userData.reprocessDirector()
    return userData


def storeInDataFrames(userData: Data):
    animeDF: pd.DataFrame = pd.DataFrame(userData.returnTable('anime'),
                                         columns=['anime_id', 'title', 'format', 'year_released',
                                                  'a_mean_score', 'director_id', 'score'])
    animeDF['a_do_I_like'] = [s >= 70 for s in animeDF['score']]

    genreDF: pd.DataFrame = pd.DataFrame(userData.returnTable('genre'),
                                         columns=['anime_id', 'Action', 'Adventure', 'Comedy', 'Drama',
                                                  'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror', 'Mahou_Shoujo',
                                                  'Mecha', 'Music', 'Mystery', 'Psychological',
                                                  'Romance', 'Slice of Life', 'Sports', 'Supernatural',
                                                  'Thriller'])

    formatDF: pd.DataFrame = pd.DataFrame(userData.returnTable('format'),
                                          columns=['anime_id', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA',
                                                   'MUSIC'])
    
    return animeDF, genreDF, formatDF