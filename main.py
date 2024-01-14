import pandas as pd

import DataGatherAndClean.graphqlqueries
from DataGatherAndClean import processGraph, director


def mainDataPrep(username: str) -> None:
    d: processGraph.Data = processGraph.Data(username)
    results: dict = DataGatherAndClean.graphqlqueries.get('AnimeLists', 'wannabe414', False)
    lst: list = results['data']['MediaListCollection']['lists']
    dropped: bool
    for x in lst:
        if x['status'] == 'PLANNING':
            continue
        elif x['status'] == 'DROPPED':
            dropped = True
        else:
            dropped = False
        processGraph.processAnime(x, d, dropped)
        processGraph.processGenre(x, d)
        processGraph.processFormat(x, d)
    animeDF: pd.DataFrame = pd.DataFrame(d.returnTable('anime'),
                                         columns=['anime_id', 'title', 'format', 'year_released', 'episodes',
                                                  'mean_score', 'director_id', 'score'])
    animeDF['do_I_Like'] = [True if s >= 70 else False for s in animeDF['score']]

    genreDF: pd.DataFrame = pd.DataFrame(d.returnTable('genre'),
                                         columns=['anime_id', 'is_Action', 'is_Adventure', 'is_Comedy', 'is_Drama',
                                                  'is_Ecchi', 'is_Sci-Fi', 'is_Fantasy', 'is_Horror', 'is_Mahou_Shoujo',
                                                  'is_Mecha', 'is_Music', 'is_Mystery', 'is_Psychological',
                                                  'is_Romance', 'is_Slice of Life', 'is_Sports', 'is_Supernatural',
                                                  'is_Thriller'])
    formatDF: pd.DataFrame = pd.DataFrame(d.returnTable('format'),
                                          columns=['anime_id', 'TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA',
                                                   'MUSIC'])

    directorDF: pd.DataFrame = director.buildDirectorDF(animeDF)

    d_MeanScores, d_DoILike = director.getDirectorStats(directorDF['director_id'], animeDF)  # lists
    directorDF['mean_score'] = d_MeanScores
    directorDF['dDoILike'] = d_DoILike

    animeDF.to_csv('animeDF.csv', index=False)
    genreDF.to_csv('genreDF.csv', index=False)
    formatDF.to_csv('formatDF.csv', index=False)
    directorDF.to_csv('directorDF.csv', index=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mainDataPrep('wannabe414')

