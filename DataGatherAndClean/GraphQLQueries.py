import time
import requests

BASE_URL: str = 'https://anilist.co'
QUERY_URL: str = 'https://graphql.anilist.co'

# a graphQL query sends in a dict of a JSON query, as shown below, along with any potential variables to plug into the
# query (specified by the $). a JSON object is returned with the same structure as the query.
# documentation can be found at https://github.com/AniList/ApiV2-GraphQL-Docs
QUERY_ANIME_DIRECTOR = '''
query ($mediaId: Int){
    Media(id: $mediaId){
        staff(sort: RELEVANCE, perPage:25){
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

QUERY_DIRECTORS_WORKS = '''
query ($directorId: Int){
    Staff(id: $directorId){
        staffMedia(sort: START_DATE, type: ANIME, page: 1, perPage: 25){
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

QUERY_USERS_ANIME_LISTS = '''
    query ($username: String){
        MediaListCollection (userName: $username, type: ANIME){
            lists{
                status
                entries{
                    media{
                        id
                        title{
                            english
                            romaji 
                        }
                        format
                        seasonYear
                        genres
                        meanScore
                        staff(sort: RELEVANCE, page:1, perPage: 6){
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
                    score(format: POINT_100)
                }
            }
        }
    }
'''

QUERY_NEW_ANIME = '''
query ($title: String, $id: Int){
    Media(search: $title, id: $id, type: ANIME){
        id
        title{
            english
            romaji
        }
        format
        startDate{
            year
        }
        genres
        meanScore
        staff(sort: RELEVANCE, page:1, perPage: 25){
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


def get(kind: str, queryVariable: str | int, rateLimit: bool = True) -> dict:
    """
    API that wraps around various graphQL queries with rate limiting included and unJSONifying included.
    :param kind: which query we want to send to aniList
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
            query = QUERY_USERS_ANIME_LISTS
            varString = 'username'
        case 'AnimeDirector':
            query = QUERY_ANIME_DIRECTOR
            varString = 'mediaId'
        case 'DirectorsWorks':
            query = QUERY_DIRECTORS_WORKS
            varString = 'directorId'
        case 'NewAnimeTitle':
            query = QUERY_NEW_ANIME
            varString = 'title'
        case 'NewAnimeID':
            query = QUERY_NEW_ANIME
            varString = 'id'
    # TODO: Refactor this library now that QUERY_NEW_ANIME is here
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
    try:
        return JSONdict['data'] is None and JSONdict['errors'][0]['status'] == 429
    except KeyError:  # only should occur on 500 errors
        print(JSONdict)
        print('500 error')
        return False
