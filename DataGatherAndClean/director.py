import pandas as pd

from DataGatherAndClean import graph
from statistics import mean


def buildDirectorDF(animeDF: pd.DataFrame):
    print(animeDF['director_id'])
    return animeDF['director_id'].drop_duplicates().to_frame(name='director_id')


def getDirectorStats(dIDs: pd.Series, animeDF: pd.DataFrame):
    directorsMeanScores = []
    directorsDoILike = []
    for directorId in dIDs:
        print(directorId)
        searchResults = graph.get('DirectorsWorks', directorId)
        directorWorks = []
        print(searchResults)
        for mediaRole in searchResults['data']['Staff']['staffMedia']['edges']:
            if mediaRole['staffRole'] == 'Director':
                directorWorks.append(mediaRole['node']['id'])
        directorsMeanScores.append(calculateDirectorsMeanScore(directorWorks, animeDF))
        directorsDoILike.append(calculateDoILikeDirector(directorWorks, animeDF))
    return directorsMeanScores, directorsDoILike


def calculateDirectorsMeanScore(directorsWorks: list, df: pd.DataFrame, ):

    directorsScores = []
    for work in directorsWorks:
        if work in df['anime_id']:
            print(work)
            score = df.query('anime_id = {work}')['score']
        else:
            searchResults = graph.get('animeScore', work)
            score = searchResults['data']['Media']['meanScore']
        directorsScores.append(score)
    return mean(directorsScores)


def calculateDoILikeDirector(directorsWorks: list, df: pd.DataFrame):

    didILike = []
    for work in directorsWorks:
        if work in df['anime_id']:
            score = df['score']
            if score >= 7:
                didILike.append(1)
            else:
                didILike.append(0)
    return mean(didILike)
