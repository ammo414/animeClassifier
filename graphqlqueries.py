queryAnimeDirectorDetails = '''
query ($mediaId: Int){
    media(id: $mediaId){
        id
        staff(sort: RELEVANCE,, perPage:25) {
            edges{
                id
                role
                node{
                    name{
                        full
                    }
                }
            }
        }
    }
}
'''

queryDirectorsWork = '''
query ($directorId: Int, $page: Int){
    staff(id: $directorId, page: $page){
        id
        staffMedia(sort: SCORE_DESC, page: 1, perPage: 25){
            edges{
                staffRole
                node{
                    int
                }
            }
        }
    }
}
'''
queryAnimeLists = '''
    query ($username: String){
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
                                id
                                role
                                node {
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
