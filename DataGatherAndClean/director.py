import pandas as pd

import DataGatherAndClean.graphqlqueries
from DataGatherAndClean import graph
from statistics import mean


def buildDirectorDF(animeDF: pd.DataFrame):
    print(animeDF['director_id'])
    return animeDF['director_id'].drop_duplicates().dropna().to_frame(name='director_id')


def getDirectorStats(dIDs: pd.Series, animeDF: pd.DataFrame):
    directorsMeanScores = []
    directorsDoILike = []
    worksScores = []
    for directorId in dIDs:
        print(directorId)
        searchResults = DataGatherAndClean.graphqlqueries.get('DirectorsWorks', directorId)
        directorWorks = []
        print(searchResults)
        for mediaRole in searchResults['data']['Staff']['staffMedia']['edges']:
            if mediaRole['staffRole'] == 'Director' or mediaRole['staffRole'] == 'Chief Director':
                directorWorks.append(mediaRole['node']['id'])
                worksScores.append(mediaRole['node']['meanScore'])
        directorsMeanScores.append(calculateDirectorsMeanScore(worksScores))
        directorsDoILike.append(calculateDoILikeDirector(directorWorks, animeDF))
    return directorsMeanScores, directorsDoILike


def calculateDirectorsMeanScore(worksScores: list):
    """
    directorsScores = []
    for work in directorsWorks:
        print(work)
        if not df.loc[df['anime_id'] == work, 'anime_id'].empty:
            score = df.loc[df['anime_id'] == work, 'mean_score'].iloc[0]
            print(score)
        else:
            searchResults = graph.get('AnimeScore', work)
            print("sr", searchResults)
            score = searchResults['data']['Media']['meanScore']
        directorsScores.append(score)
    directorsScores = [s for s in directorsScores if s is not None]
    if len(directorsScores) > 0:
        return mean(directorsScores)
    else:
        return 0
    """
    worksScores = [s for s in worksScores if s is not None]
    if len(worksScores) > 0:
        return mean(worksScores)
    else:
        return 0


def calculateDoILikeDirector(directorsWorks: list, df: pd.DataFrame):

    didILike = []
    for work in directorsWorks:
        if not df.loc[df['anime_id'] == work, 'anime_id'].empty:
            print('work:', work)
            score = df.loc[df['anime_id'] == work, 'score'].iloc[0]
            if score >= 70:
                didILike.append(1)
            else:
                didILike.append(0)
    if len(didILike) > 0:
        return mean(didILike)
    else:
        return 0


def findDirector(entry: dict) -> int:
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
    return directorId
