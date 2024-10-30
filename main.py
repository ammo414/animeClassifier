from pathlib import Path
from datetime import date

import pandas as pd

from DataGatherAndClean import processGraph, directorHandling, animeData
from DataTrainAndTest import buildModels
from DeployModel import httpServer
try:
    from constants import USERNAME
except ModuleNotFoundError:
    USERNAME = None


def mainDataPrep(username: str) -> None:
    ## gather data and begin processing
    userData: animeData.Data = processGraph.getAllData(username)

    ## store data in pandas dataframes
    animeDF: pd.DataFrame
    genreDF: pd.DataFrame
    formatDF: pd.DataFrame

    animeDF, genreDF, formatDF = processGraph.storeInDataFrames(userData)
    
    ## get director data and store into pandas dataframe
    print('Processing Director Data')
    directorDF = directorHandling.finalizeDirectorDF(animeDF)

    ## pandas dataframe to csv to be picked up by buildModels
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


if __name__ == '__main__':
    run_server = input("Run Server?: (y/n). If n, then trains models.\n")
    if "y" in run_server.lower():
        httpServer.mainCall()
    else:
        if out_of_date():
            userName = USERNAME
            if userName is None:
                userName = input("Username?:\n")
            mainDataPrep('userName')
            buildModels.mainTrainModels()
            log_queried_date()
        else:
            print("Model Not Out of Date; No Need to Retrain")
