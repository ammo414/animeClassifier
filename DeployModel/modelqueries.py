QUERY_NEW_ANIME = '''
query ($mediaId: Int){
    Media(id: $mediaId){
        staff(sort: RELEVANCE, perPage: 25){
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
        format
        seasonYear
        genres
        meanScore
    }
}
'''

