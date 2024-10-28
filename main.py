from pathlib import Path
from datetime import date

import pandas as pd

import DataGatherAndClean.GraphQLQueries
from DataGatherAndClean import processGraph, directorHandling
from DataTrainAndTest import buildModels
from DeployModel import httpServer


def mainDataPrep(username: str) -> None:
    userData: processGraph.Data = processGraph.Data(username)
    results: dict = DataGatherAndClean.GraphQLQueries.get('AnimeLists', username, False)
    listOfLists: list = results['data']['MediaListCollection']['lists']
    dropped: bool
    for animeList in listOfLists:
        if animeList['status'] == 'PLANNING':
            continue  # don't want to use planning to watch anime as they don't have reliable scores
        dropped = animeList['status'] == 'DROPPED'
        for anime in animeList['entries']:
            processGraph.processAnime(anime, userData, dropped)
            processGraph.processGenre(anime, userData)
            processGraph.processFormat(anime, userData)
    userData.reprocessDirector()

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
    print('Processing Director Data')
    directorDF: pd.DataFrame = directorHandling.buildDirectorDF(animeDF)

    d_MeanScores, d_DoILike = directorHandling.calculateDirectorStats(directorDF['director_id'], animeDF)  # lists
    directorDF['d_mean_score'] = d_MeanScores
    directorDF['d_do_I_like'] = d_DoILike

    animeDF.to_csv('./data/animeDF.csv', index=False)
    genreDF.to_csv('./data/genreDF.csv', index=False)
    formatDF.to_csv('./data/formatDF.csv', index=False)
    directorDF.to_csv('./data/directorDF.csv', index=False)

def out_of_date():
    # if the models were last trained more than 90 days ago, train again
    # if when_trained.csv has not been created, create it and return False 
    today = date.today()
    data_dir = Path('./data')
    log_file = Path('./data/when_trained.csv')
    
    if not data_dir.is_dir():
        data_dir.mkdir(parents=True)
    if not log_file.is_file():
        with open(str(log_file), "w", encoding="utf-8") as file:
            file.write(str(today.strftime("%Y,%m,%d")))
            return False

    with open(str(log_file), "r", encoding="utf-8") as file:
        last_l = [int(x) for x in file.readlines()[-1].split(",")]
        last_log_ago = today - date(*last_l)
        return last_log_ago.days >= 90
     
def log_queried_date():
    today = date.today()
    with open('./data/when_trained.csv', "a", encoding="utf-8") as file:
        file.write("\n" + str(today.strftime("%Y,%m,%d")))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_server = input("Run Server?: (y/n) ")
    if "y" in run_server.lower():
        httpServer.mainCall()
    else:
        if out_of_date():
            #mainDataPrep('wannabe414')
            buildModels.mainTrainModels()
            log_queried_date()
        else:
            print("Model Not Out of Date; No Need to Retrain")
