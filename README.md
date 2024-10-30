I like watching anime. I've watched a lot of anime and documented that data in AniList. I'd like to watch more but struggle to reliably find shows I like. So I created this machine learning pipeline!

I query my profile with [AniLits's GraphQL API](https://github.com/AniList/ApiV2-GraphQL-Docs), store the data in a pandas dataframe, and train an ensemble consisting of a logistic classifier and a random forest on the data to predict if I will like a given show. I implemented a basic API with Flask (not public, sorry) so that I can query the model whenever.

## DataGatherAndClean
I store all used queries as strings in `GraphQLQueries` as well as a function, `get` that takes care of figuring out the right query string to use, rate limiting issues, and unpacking the response JSON. Since, outside of username, this program never asks for user input, I'm not too worried about GraphQL injection issues, though it can theoretically be a concern.

I also use director data as a feature. This one is complicated: since just using the director's ID is pointless, I look at the anime that the director directed and see if I like any of them. If I like most of the anime that they directed, then I will say that I like the director. I also create a column of the mean of the mean scores of all the anime they directed. This way, even if I never watched a show directed by them, I can still gleam insight into how much I might like their shows.

I decided on looking at the anime's format, genre, year released, and mean score for future predictions.

Since genre and format are categorical, I manually dummy variabled them. I didn't realize pandas had a dummy variable function when I wrote that, but it works well and the code looks nice so I'll keep it.

## DataTrainAndTest
I used scikit-learn to train my models on the above features. Since, when querying for a new anime, there's no guarantee that Director data will exist, I had to create two ensembles: one with director data and one without. I pickled the models so that I could pick up again the models at any point in the future. 

## DeployModel
Using Flask, I implented a basic API (still in debug mode) so that I can give my app either an animeID or an AniList URL or an anime title and get a prediction. So far, I've agreed with the predictions! Since the focus of this project was not on learning how to implement a server, this part is very unpolished and will likely stay that way.

# TODO:
- [ ] Better document the model development process/ showcase my EDA.

- [ ] Implement SQL database instead of using .CSVs.

- [ ] Implement a way to continously improve the model -- introduce continous injestion of new ratings (once a quarter?) and retrain the model with that new data. 
