import pandas as pd

import DataGatherAndClean.GraphQLQueries
from DataGatherAndClean import processGraph, directorHandling
from DataTrainAndTest import buildModels


def mainDataPrep(username: str) -> None:
    userData: processGraph.Data = processGraph.Data(username)
    results: dict = DataGatherAndClean.GraphQLQueries.get('AnimeLists', username, False)
    listOfLists: list = results['data']['MediaListCollection']['lists']
    dropped: bool
    for animeList in listOfLists:
        if animeList['status'] == 'PLANNING':
            continue  # don't want to use planning to watch anime as they don't have reliable scores
        elif animeList['status'] == 'DROPPED':
            dropped = True
        else:
            dropped = False
        for anime in animeList['entries']:
            processGraph.processAnime(anime, userData, dropped)
            processGraph.processGenre(anime, userData)
            processGraph.processFormat(anime, userData)
    userData.reprocessDirector()

    animeDF: pd.DataFrame = pd.DataFrame(userData.returnTable('anime'),
                                         columns=['anime_id', 'title', 'format', 'year_released',
                                                  'a_mean_score', 'director_id', 'score'])
    animeDF['a_do_I_like'] = [True if s >= 70 else False for s in animeDF['score']]

    genreDF: pd.DataFrame = pd.DataFrame(userData.returnTable('genre'),
                                         columns=['anime_id', 'Action', 'Adventure', 'Comedy', 'Drama',
                                                  'Ecchi', 'Sci-Fi', 'Fantasy', 'Horror', 'Mahou_Shoujo',
                                                  'Mecha', 'Music', 'Mystery', 'Psychological',
                                                  'Romance', 'Slice of Life', 'Sports', 'Supernatural',
                                                  'Thriller'])
    formatDF: pd.DataFrame = pd.DataFrame(userData.returnTable('format'),
                                          columns=['anime_id', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA',
                                                   'MUSIC'])
    print('Processing Director Data')
    directorDF: pd.DataFrame = directorHandling.buildDirectorDF(animeDF)

    d_MeanScores, d_DoILike = directorHandling.calculateDirectorStats(directorDF['director_id'], animeDF)  # lists
    directorDF['d_mean_score'] = d_MeanScores
    directorDF['d_do_I_like'] = d_DoILike

    animeDF.to_csv('animeDF.csv', index=False)
    genreDF.to_csv('genreDF.csv', index=False)
    formatDF.to_csv('formatDF.csv', index=False)
    directorDF.to_csv('directorDF.csv', index=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mainDataPrep('wannabe414')
    buildModels.mainTrainModels()


