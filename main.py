import pandas as pd

from DataGatherAndClean import graph, director


def main(username: str) -> None:
    d: graph.Data = graph.Data(username)
    results: dict = graph.get('AnimeLists', 'wannabe414', False)
    lst: list = results['data']['MediaListCollection']['lists']
    for x in lst:
        status = x['status']
        # if status == 'COMPLETED' or status == 'WATCHING':
        #    graph.processAnime(x, d)
        #    graph.processGenre(x, d)
        #  TODO: filter out plan to watch since they dont have a score
        if status == 'DROPPED':
            graph.processAnime(x, d, True)
            graph.processGenre(x, d)
    print(d.animeData)
    animeDF: pd.DataFrame = pd.DataFrame(d.returnTable('anime'),
                                         columns=['anime_id', 'title', 'format', 'year_released', 'episodes',
                                                  'mean_score', 'director_id', 'score'])
    genreDF: pd.DataFrame = pd.DataFrame(d.returnTable('genre'),
                                         columns=['anime_id', 'is_Action', 'is_Adventure', 'is_Comedy', 'is_Drama',
                                                  'is_Ecchi', 'is_Sci-Fi', 'is_Fantasy', 'is_Horror', 'is_Mahou_Shoujo',
                                                  'is_Mecha', 'is_Music', 'is_Mystery', 'is_Psychological',
                                                  'is_Romance', 'is_Slice of Life', 'is_Sports', 'is_Supernatural',
                                                  'is_Thriller'])

    animeDF['do_I_Like'] = [True if s >= 70 else False for s in animeDF['score']]

    directorDF: pd.DataFrame = director.buildDirectorDF(animeDF)
    print(directorDF.head())

    d_MeanScores, d_DoILike = director.getDirectorStats(directorDF)  # lists
    directorDF['mean_score'] = d_MeanScores
    directorDF['dDoILike'] = d_DoILike

    print(genreDF.head(10))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main('wannabe414')
