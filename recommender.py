# import constants
from evaluation import evaluateMAE, evaluateUserPrecisionRecall
# from similarity import computeFeaturesSimilarity
from utils import evaluateAverage, getUserMovies, getEliteTestRatingSet, \
    getRandomMovieSet, getUserBaseline, getItemBaseline, getMovieRatings1, getMovieRatings2
from sklearn.metrics.pairwise import cosine_similarity
from opening_feat import load_features
import numpy as np
import sqlite3

# conn = sqlite3.connect('database.db')

DEEP_FEATURES = load_features('resnet_152_lstm_128.dct')
LOW_LEVEL_FEATURES = load_features('low_level_dict.bin')

AVG_ALL_RATINGS = 3.51611876907599


# def collaborative(movieI, movieJ):
#
#     global conn
#
#     # select all the ratings of movie I from users that also rated movie J
#     ratingsI = np.array([x[0] for x in getMovieRatings1(conn, movieI[1], movieJ[1])])
#     ratingsJ = np.array([x[0] for x in getMovieRatings2(conn, movieI[1], movieJ[1])])
#
#     if len(ratingsI) > 0 and len(ratingsJ) > 0:
#         return cosine_similarity([ratingsI], [ratingsJ])
#     return 0


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


def hybrid(movieI, movieJ):

    global LOW_LEVEL_FEATURES, DEEP_FEATURES

    traileri = movieI[3]
    trailerj = movieJ[3]

    try:
        featuresI = LOW_LEVEL_FEATURES[traileri]
        featuresJ = LOW_LEVEL_FEATURES[trailerj]
        featuresDeepI = DEEP_FEATURES[traileri]
        featuresDeepJ = DEEP_FEATURES[trailerj]

        vI = np.hstack((featuresI, featuresDeepI))
        vJ = np.hstack((featuresJ, featuresDeepJ))

        cos = cosine_similarity([vI], [vJ])

        return cos
    except KeyError:
        return 0


def recommend(conn, Users, N, simFunction):

    SumRecall, SumPrecision, SumMAE = 0, 0, 0
    count = 0

    for user in Users:
        # print "Testing for User", user[0], "..."
        count += 1
        if count % 50 == 0:
            print "50 users evaluated"

        userBaseline = getUserBaseline(conn, user[0])
        userMovies = getUserMovies(conn, user[0])
        test = getEliteTestRatingSet(conn, user[0])

        if len(test) == 0:
            continue

        # print len(test), "items in elite set."
        hits = 0
        # For each item rated high by the user
        for eliteMovie in test:
            predictions = []

            prediction = predictUserRating(conn, userMovies, eliteMovie, simFunction, userBaseline)
            predictions.append((eliteMovie[1], eliteMovie[2], prediction))

            randomMovies = getRandomMovieSet(conn, user[0])

            for randomMovie in randomMovies:
                try:
                    prediction = predictUserRating(conn, userMovies, randomMovie, simFunction, userBaseline)
                    predictions.append((randomMovie[1], randomMovie[2], prediction))
                except KeyError:
                    continue

            predictions_ids = [x[0] for x in sorted(predictions, key=lambda tup: tup[2], reverse=True)]
            eliteIndex = predictions_ids.index(eliteMovie[1])
            if eliteIndex <= N:
                hits += 1

        # print hits, "hits"

        recall = hits / float(len(test))
        SumRecall += recall
        SumPrecision += (recall / float(N))
        SumMAE += evaluateMAE(conn, user[0], predictions)

    size = len(Users)
    avgRecall = evaluateAverage(SumRecall, size)
    avgPrecision = evaluateAverage(SumPrecision, size)
    avgMAE = evaluateAverage(SumMAE, size)

    return avgPrecision, avgRecall, avgMAE


def predictUserRating(conn, userMovies, movieI, simFunction, userBaseline):

    global AVG_ALL_RATINGS

    SumSimilarityTimesRating = float(0)
    SumSimilarity = float(0)
    prediction = 0
    AllSimilarities = [(movieJ, simFunction(movieI, movieJ)) for movieJ in userMovies]
    topSimilar = sorted(AllSimilarities, key=lambda tup: tup[1], reverse=True)[:30]

    itemBaseline = getItemBaseline(conn, userBaseline, movieI[1])
    # print userBaseline, itemBaseline

    try:
        baselineUserItem = AVG_ALL_RATINGS + userBaseline + itemBaseline
    except TypeError:
        print "Type Error", userBaseline, "Movie Id", movieI[1]
        baselineUserItem = AVG_ALL_RATINGS + userBaseline

    for movieJ, sim in topSimilar:
        SumSimilarityTimesRating += (sim * (float(movieJ[0] - baselineUserItem)))  # similarity * user rating
        SumSimilarity += abs(sim)

    if (SumSimilarityTimesRating != 0 and SumSimilarity != 0):
        prediction = (SumSimilarityTimesRating / SumSimilarity) + baselineUserItem

    return prediction

# if __name__ == '__main__':
#     main()
