from statistics import mean

import pandas as pd

from DataGatherAndClean.GraphQLQueries import get


def buildDirectorDF(animeDF: pd.DataFrame) -> pd.DataFrame:
    """
    creates DataFrame of just primary key column of director_id, to be built upon later
    :param animeDF: anime DataFrame with 'director_id' column
    :return: directorDF with only one column
    """
    return animeDF['director_id'].drop_duplicates().dropna().to_frame(name='director_id')


def calculateDirectorStats(dIDs: pd.Series, animeDF: pd.DataFrame) -> tuple:
    """
    gets the mean mean score of all anime the director directed and percentage of anime I liked by them.
    however, the GraphQL only lets me grab the first n anime that an employee worked on (not necessarily as a director).
    since I don't want to hit the database too much, we are only sampling from however many of the first 25 of their
    works they directed, so this is not great but it probably is the best.
    :param dIDs: director_id column
    :param animeDF: anime DataFrame
    :return: mean mean score of director's animes and percentage of animes I liked by them
    """
    directorsMeanScores = []
    directorsDoILike = []
    for directorId in dIDs.to_list():
        searchResults = get('DirectorsWorks', directorId)  # only looks at first 25 media that they were staffed to
        print(f'Processing directorID {directorId}')
        worksOfDirector = []
        scoresOfAllWorks = []
        for mediaRole in searchResults['data']['Staff']['staffMedia']['edges']:
            if mediaRole['staffRole'] == 'Director' or mediaRole['staffRole'] == 'Chief Director':
                worksOfDirector.append(mediaRole['node']['id'])
                scoresOfAllWorks.append(mediaRole['node']['meanScore'])
        #  for each instance of the director_id, find animeID
        #  needs to be sped up # does this still need to be sped up?
        worksFromAnimeDF: pd.DataFrame = animeDF.loc[animeDF['director_id'] == directorId]
        animeIds = worksFromAnimeDF['anime_id']
        meanScores = worksFromAnimeDF['a_mean_score']
        animeIds.reset_index(drop=True, inplace=True)
        meanScores.reset_index(drop=True, inplace=True)
        #  since animeIDs and meanScores were indexed the same, iterating through one effectively iterates through the
        #  other as well. since we already have data on anime that I like, adding the animes directed by that director
        #  from animeDF to the list of directorsWorks gives us some more data to work with.
        for iterate, aId in enumerate(animeIds):
            if aId not in worksOfDirector:
                worksOfDirector.append(aId)
                scoresOfAllWorks.append(meanScores[iterate])

        directorsMeanScores.append(calculateDirectorsMeanScore(scoresOfAllWorks))
        directorsDoILike.append(calculateDoILikeDirector(worksOfDirector, animeDF))

    return directorsMeanScores, directorsDoILike


def calculateDirectorsMeanScore(worksScores: list) -> int:
    """
    calculates the mean score of the aniList's community's mean scores of all the director's known works
    :param worksScores: mean score of each of the the director's works
    :return: mean score
    """
    worksScores = [s for s in worksScores if s is not None]
    if len(worksScores) > 0:
        return int(mean(worksScores))
    return 0


def calculateDoILikeDirector(directorsWorks: list, animeDF: pd.DataFrame) -> int:
    """
    gets percentage of anime (aka work) I like by the director
    :param directorsWorks: list of works by the director
    :param animeDF: animeDF with columns ['anime_id'] and ['score']
    :return: number between 0 and 100, inclusive, calculated by (number of works I liked/total number of works)
    """
    didILike = []
    for work in directorsWorks:
        if not animeDF.loc[animeDF['anime_id'] == work, 'anime_id'].empty:  # if work is in animeDF
            score = animeDF.loc[animeDF['anime_id'] == work, 'score'].iloc[0]
            if score >= 70:
                didILike.append(1)
            else:
                didILike.append(0)
    if len(didILike) > 0:
        return int(mean(didILike)*100)
    return 0


def findDirector(entry: dict) -> int | None:
    """
    searches through anime json for the director, if any
    :param entry: json query result from aniList's GraphQL
    :return: director's Id or None if cannot be found.
    """
    directorId: str | None = None
    chiefDirectorId: str | None = None

    media: str
    if 'media' in entry:
        media = 'media'
    else:
        media = 'Media'  # depending on the query, we either get 'media' or 'Media'
    for staff in entry[media]['staff']['edges']:
        if staff['role'].strip() == 'Director':
            directorId = staff['node']['id']
            break
        if staff['role'].strip() == 'Chief Director':
            chiefDirectorId = staff['node']['id']

    if directorId is None:
        directorId = chiefDirectorId
    try:
        return int(directorId)
    except TypeError:  # should only occur if directorId is None, but just in case
        return directorId


def isDirectorInDF(directorId: int, directorDF: pd.DataFrame) -> bool:
    """
    determines if director is in a DataFrame
    :param directorId: director ID
    :param directorDF: DataFrame with ['director_id'] column
    :return:
    """

    return directorId in directorDF['director_id'].array


def pullDirectorStatsFromDF(directorId: int, directorDF: pd.DataFrame) -> list:
    """
    pulls director's two stats (do I like them, and mean score) from DataFrame
    :param directorDF: DataFrame with director_id, d_do_I_like, and d_mean_score
    :param directorId: director's ID
    :return: list of [d_do_I_like, d_mean_score]
    """
    d_doILike = directorDF.loc[directorDF['director_id'] == directorId, 'd_do_I_like'].iloc[0]
    d_meanScore = directorDF.loc[directorDF['director_id'] == directorId, 'd_mean_score'].iloc[0]
    return [d_doILike, d_meanScore]
