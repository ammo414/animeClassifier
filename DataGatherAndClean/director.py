import pandas as pd

from DataGatherAndClean import graph
from statistics import mean


def buildDirectorDF(animeDF: pd.DataFrame):
    print(animeDF['director_id'])
    return animeDF['director_id'].to_frame(name='director_id')


def getDirectorStats(df: pd.DataFrame):
    dIDs = df['director_id']
    directorsMeanScores = []
    directorsDoILike = []
    for directorId in dIDs:
        print(directorId)
        searchResults = graph.get('DirectorsWorks', directorId)
        directorWorks = []
        print(searchResults)
        for media in searchResults['data']['Staff']['staffMedia']:
            if media['edges']['staffRole'] == 'Director':
                directorWorks.append(media['edges']['node']['id'])
        directorsMeanScores.append(calculateDirectorsMeanScore(directorWorks, df))
        directorsDoILike.append(calculateDoILikeDirector(directorWorks, df))
    return directorsMeanScores, directorsDoILike


def calculateDirectorsMeanScore(directorsWorks: list, df: pd.DataFrame):

    directorsScores = []
    for work in directorsWorks:
        if work in df['anime_id']:
            score = df.query('anime_id = {work}')['anime_id']
        else:
            score = graph.get('animeScore', work)
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
