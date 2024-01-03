import pandas as pd

import DataGatherAndClean.graphqlqueries
from DataGatherAndClean import graph, director


def main(username: str) -> None:
    d: graph.Data = graph.Data(username)
    results: dict = DataGatherAndClean.graphqlqueries.get('AnimeLists', 'wannabe414', False)
    lst: list = results['data']['MediaListCollection']['lists']
    dropped: bool
    for x in lst:
        if x['status'] == 'DROPPED':
            dropped = True
        elif x['status'] == 'PLANNING':
            continue
        else:
            dropped = False
        # if status == 'COMPLETED' or status == 'WATCHING':
        #    graph.processAnime(x, d)
        #    graph.processGenre(x, d)
        graph.processAnime(x, d, dropped)
        graph.processGenre(x, d)
        graph.processFormat(x, d)
    print(d.animeData)
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

    directorDF: pd.DataFrame = director.buildDirectorDF(animeDF)

    d_MeanScores, d_DoILike = director.getDirectorStats(directorDF['director_id'], animeDF)  # lists
    directorDF['mean_score'] = d_MeanScores
    directorDF['dDoILike'] = d_DoILike

    animeDF.to_csv('animeDF.csv')
    genreDF.to_csv('genreDF.csv')
    directorDF.to_csv("directorDF.csv")

    print(directorDF.head())
    print(genreDF.head(10))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('wannabe414')
