import time

import requests

from DataGatherAndClean.graph import QUERY_URL

queryAnimeDirector = '''
query ($mediaId: Int){
    Media(id: $mediaId){
        staff(sort: RELEVANCE, perPage:25) {
            edges{
                role
                node{
                    id
                    name{
                        full
                    }
                }
            }
        }
    }
}
'''

queryDirectorsWorks = '''
query ($directorId: Int){
    Staff(id: $directorId){
        staffMedia(sort: SCORE_DESC, page: 1, perPage: 25){
            edges{
                staffRole
                node{
                    id
                    meanScore
                }
            }
        }
    }
}
'''

queryAnimeScore = '''
query ($mediaId: Int){
    Media (id: $mediaId) {
        meanScore 
    }
}
'''

queryAnimeLists = '''
    query ($username: String) {
        MediaListCollection (userName: $username, type: ANIME) {
            lists {
                status
                entries {
                    media {
                        id
                        title {
                            english
                            romaji 
                        }
                        format
                        seasonYear
                        episodes
                        genres
                        meanScore
                        staff(sort: RELEVANCE, page:1, perPage: 6) {
                            edges{
                                role
                                node {
                                    id
                                    name {
                                        full
                                    }
                                }
                            }
                        }
                    }
                    score(format: POINT_100)
                }
            }
        }
    }
'''


def get(kind: str, queryVariable: str | int, rateLimit: bool = True) -> dict:
    """
    for an aniList username, query for all their watchlists
    :param kind: which query
    :param queryVariable: variables for the query
    :param rateLimit:
    :return: list of watchlists
    """
    response: requests.Response
    searchResults: dict
    animeLists: list
    query: str = ""
    varString: str = ""
    match kind:
        case 'AnimeLists':
            query = queryAnimeLists
            varString = 'username'
        case 'AnimeDirector':
            query = queryAnimeDirector
            varString = 'mediaId'
        case 'DirectorsWorks':
            query = queryDirectorsWorks
            varString = 'directorId'
    if rateLimit:
        time.sleep(2)
    response = requests.post(QUERY_URL, json={'query': query, 'variables': {varString: queryVariable}})
    searchResults = response.json()
    if rateLimitHit(searchResults):
        print('hit the rate limit, try again')
    return searchResults


def rateLimitHit(JSONdict: dict) -> bool:
    """
    determines if we hit the rate limit
    :param JSONdict: dict deserialized from a json string
    :return: boolean of if we hit the rate limit
    """
    return JSONdict['data'] is None and JSONdict['errors'][0]['status'] == 429
