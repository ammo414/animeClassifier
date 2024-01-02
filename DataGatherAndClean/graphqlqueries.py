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
                }
            }
        }
    }
}
'''

queryAnimeScore = '''
query ($animeId: String){
    Media {
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
