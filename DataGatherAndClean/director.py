import pandas
import pandas as pd

from DataGatherAndClean.graphqlqueries import get
from statistics import mean


def buildDirectorDF(animeDF: pd.DataFrame) -> pd.DataFrame:
    """
    creates DataFrame of just primary key column of director_id
    :param animeDF:
    :return:
    """
    return animeDF['director_id'].drop_duplicates().dropna().to_frame(name='director_id')


def getDirectorStats(dIDs: pd.Series, animeDF: pd.DataFrame) -> tuple:
    """
    gets the mean score of all anime the director directed and percentage of anime I liked by them
    :param dIDs: director_id column
    :param animeDF: anime DataFrame
    :return:
    """
    directorsMeanScores = []
    directorsDoILike = []
    for directorId in dIDs.to_list():
        print('director:', directorId)
        searchResults = get('DirectorsWorks', directorId)  # only looks at first 25 media that they were staffed to
        directorWorks = []
        worksScores = []
        for mediaRole in searchResults['data']['Staff']['staffMedia']['edges']:
            if mediaRole['staffRole'] == 'Director' or mediaRole['staffRole'] == 'Chief Director':
                print('media:', mediaRole['node']['id'])
                directorWorks.append(mediaRole['node']['id'])
                worksScores.append(mediaRole['node']['meanScore'])
        #  for each instance of the director_id, find animeID
        #  needs to be sped up
        worksFromAnimeDF: pandas.DataFrame = animeDF.loc[animeDF['director_id'] == directorId]
        animeIds = worksFromAnimeDF['anime_id']
        meanScores = worksFromAnimeDF['mean_score']
        animeIds.reset_index(drop=True)
        meanScores.reset_index(drop=True)

        for iterate, aId in enumerate(animeIds):
            if aId not in directorWorks:
                directorWorks.append(aId)
                worksScores.append(meanScores[iterate])
                #  TODO TEST AND FIX THIS

        directorsMeanScores.append(calculateDirectorsMeanScore(worksScores))
        directorsDoILike.append(calculateDoILikeDirector(directorWorks, animeDF))

    return directorsMeanScores, directorsDoILike


def calculateDirectorsMeanScore(worksScores: list) -> int:
    """
    calculates the mean score of the mean scores of all the directors works
    :param worksScores: mean score of all the director's works
    :return:
    """
    worksScores = [s for s in worksScores if s is not None]
    if len(worksScores) > 0:
        return int(mean(worksScores))
    else:
        return 0


def calculateDoILikeDirector(directorsWorks: list, df: pd.DataFrame) -> int:
    """
    gets percentage of anime I like by the director
    :param directorsWorks:
    :param df:
    :return:
    """
    didILike = []
    for work in directorsWorks:
        if not df.loc[df['anime_id'] == work, 'anime_id'].empty:  # if work is in animeDF
            score = df.loc[df['anime_id'] == work, 'score'].iloc[0]
            if score >= 70:
                didILike.append(1)
            else:
                didILike.append(0)
    if len(didILike) > 0:
        return int(mean(didILike)*100)
    else:
        return 0


def findDirector(entry: dict) -> int | None:
    """
    searches through anime json for the director, if any
    :param entry:
    :return:
    """
    directorId = None
    chiefDirectorId = None
    try:
        for staff in entry['media']['staff']['edges']:
            if staff['role'].strip() == 'Director':
                directorId = staff['node']['id']
                break
            if staff['role'].strip() == 'Chief Director':
                chiefDirectorId = staff['node']['id']

    except KeyError:
        for staff in entry['Media']['staff']['edges']:
            if staff['role'].strip() == 'Director':
                directorId = staff['node']['id']
                break
            if staff['role'].strip() == 'Chief Director':
                chiefDirectorId = staff['node']['id']
    if directorId is None:
        directorId = chiefDirectorId
    try:
        return int(directorId)
    except TypeError:
        return directorId  # should always be None, but just in case
