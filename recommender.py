# import constants
from evaluation import evaluateMAE, evaluateUserPrecisionRecall
# from similarity import computeFeaturesSimilarity
from utils import evaluateAverage, getUserMovies, getEliteTestRatingSet, getRandomMovieSet, getUserBaseline, getItemBaseline
from sklearn.metrics.pairwise import cosine_similarity
from opening_feat import load_features

DEEP_FEATURES = load_features('resnet_152_lstm_128.dct')
LOW_LEVEL_FEATURES = load_features('low_level_dict.bin')

AVG_ALL_RATINGS = 3.51611876907599

# for every item to predict, determine the class based on the proximity of k items that the user rated
# def contentBasedKnn(Users, SelectedMovies, k=1):
#     for user in Users:
#         print "Computing for User ", user[0], "..."
#         for movieI in SelectedMovies:
#             AllSimilarities = []
#             c = constants.conn.cursor()
#             c.execute(constants.getQueryUserMovies(), (user[0], movieI[constants.INDEX_COLUMN_ID],))
#             for userMovie in c.fetchall():
#                 sim = computeFeaturesSimilarity(movieI, userMovie)
#                 AllSimilarities.append((userMovie[constants.INDEX_COLUMN_TITLE+1], sim))
#             print movieI[constants.INDEX_COLUMN_TITLE]
#             print AllSimilarities
#             return

def lowlevel(movieI, movieJ):

    global LOW_LEVEL_FEATURES

    traileri = movieI[3]
    trailerj = movieJ[3]

    try:
        featuresI = LOW_LEVEL_FEATURES[traileri]
        featuresJ = LOW_LEVEL_FEATURES[trailerj]
    except KeyError:
        return 0

    cos = cosine_similarity([featuresI], [featuresJ])

    return cos[0][0]

def deep(movieI, movieJ):

    global DEEP_FEATURES

    traileri = movieI[3]
    trailerj = movieJ[3]

    featuresI = DEEP_FEATURES[traileri]
    featuresJ = DEEP_FEATURES[trailerj]

    return cosine_similarity([featuresI], [featuresJ])[0][0]

def recommend(conn, Users, SelectedMovies, simFunction):

    # SumMAE, SumRecall, SumPrecision = 0, 0, 0
    SumRecall, SumPrecision = 0, 0
    N = 10

    for user in Users:
        print "Training for User", user[0], "..."
        # predictions = []
        userBaseline = getUserBaseline(conn, user[0])
        userMovies = getUserMovies(conn, user[0])
        #Predict rating for each movie - Training
        # for movieI in SelectedMovies:
        #     prediction = predictUserRating(conn, user, movieI, simFunction)
        #     predictions.append((movieI[0], movieI[1], prediction))
        #
        # print "Training end."

        # topPredictions = sorted(predictions, key=lambda tup: tup[2], reverse=True)[:PREDICTION_LIST_SIZE] # 2 is the index of the rating
        # print "Top Predictions ", topPredictions
        # print topPredictions
        # exit()
        # SumMAE += evaluateMAE(conn, user[0], predictions) #predicted ratings for the same movies that the user rated
        # predictionsIds = [int(x[0]) for x in predictions]

        test = getEliteTestRatingSet(conn, user[0])

        if len(test) == 0:
            continue

        print len(test), "items in elite set."
        eliteMoviesIds = [x[1] for x in test]

        hits = 0
        # For each item rated high by the user
        for eliteMovie in test:
            predictions = []
            print "Elite Movie", eliteMovie

            prediction = predictUserRating(conn, userMovies, eliteMovie, simFunction, userBaseline)
            # print "Prediction", prediction
            # exit()
            predictions.append((eliteMovie[1], eliteMovie[2], prediction))

            randomMovies = getRandomMovieSet(conn, user[0])

            for randomMovie in randomMovies:
                prediction = predictUserRating(conn, userMovies, randomMovie, simFunction, userBaseline)
                predictions.append((randomMovie[1], randomMovie[2], prediction))

            # print "Test Set", test
            print "Sorted Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)
            predictions_ids = [x[0] for x in sorted(predictions, key=lambda tup: tup[2], reverse=True)]
            # print "IDS:", predictions_ids
            eliteIndex = predictions_ids.index(eliteMovie[1])
            print eliteIndex, "\n"
            if eliteIndex <= N:
                hits += 1
            # print indexes
        # exit()

        print hits, "hits"

        SumRecall += hits / float(len(test))
        SumPrecision += SumRecall / float(N)

        print "Test end."

        # recall, precision = evaluateUserPrecisionRecall(conn, user[0], predictionsIds, PREDICTION_LIST_SIZE)
        # SumRecall += recall
        # SumPrecision += precision

    size = len(Users)
    # avgMAE = evaluateAverage(SumMAE, size)
    avgRecall = evaluateAverage(SumRecall, size)
    avgPrecision = evaluateAverage(SumPrecision, size)

    return avgPrecision, avgRecall
    # return avgMAE, avgPrecision, avgRecall


def predictUserRating(conn, userMovies, movieI, simFunction, userBaseline):

    global AVG_ALL_RATINGS

    SumSimilarityTimesRating = float(0)
    SumSimilarity = float(0)
    prediction = 0
    AllSimilarities = [(movieJ, simFunction(movieI, movieJ)) for movieJ in userMovies]
    topSimilar = sorted(AllSimilarities, key=lambda tup: tup[1], reverse=True)[:30]

    # TODO multiply the similarity by the division of the item average rating by the largest average rating of all items
    itemBaseline = getItemBaseline(conn, userBaseline, movieI[1])

    # print userBaseline, itemBaseline

    try:
        baselineUserItem = AVG_ALL_RATINGS + userBaseline + itemBaseline
    except TypeError:
        print "Type Error", userBaseline, "Movie Id", movieI[1]
        baselineUserItem = AVG_ALL_RATINGS + userBaseline

    for movieJ, sim in topSimilar:
        # sim = simFunction(movieI, movieJ)
        # print "Similarity", sim, "Movie I", movieI, "Movie J", movieJ
        SumSimilarityTimesRating += (sim * (float(movieJ[0] - baselineUserItem)))  # similarity * user rating
        SumSimilarity += abs(sim)
        # SumSimilarity += sim

    if (SumSimilarityTimesRating != 0 and SumSimilarity != 0):
        prediction = (SumSimilarityTimesRating / SumSimilarity) + baselineUserItem

    return prediction

# if __name__ == '__main__':
#     main()
