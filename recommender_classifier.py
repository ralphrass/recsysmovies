# import constants
from evaluation import evaluateMAE, evaluateUserPrecisionRecall
# from similarity import computeFeaturesSimilarity
import utils
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn import svm
import random
import sqlite3

AVG_ALL_RATINGS = 3.51611876907599
STD_DEVIATION = 1.098732183

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


def cosine(movieI, movieJ, feature_vector):

    traileri = movieI[0]
    trailerj = movieJ[0]

    featuresI = feature_vector[traileri]
    featuresJ = feature_vector[trailerj]

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


def recommend_random(user_datasets, N):

    global AVG_ALL_RATINGS, STD_DEVIATION

    conn = sqlite3.connect('database.db')

    SumRecall, SumPrecision, SumMAE = 0, 0, 0

    for user, datasets in user_datasets.iteritems():
        # print "Training User", user[0], " model..."

        if len(datasets['elite_test']) == 0:
            continue

        random_movies = datasets['random']

        hits = 0
        # For each item rated high by the user
        for eliteMovie in datasets['elite_test']:
            predictions = []
            # print "Elite Movie", eliteMovie
            prediction = random.uniform(0.5, 5)
            # prediction = random.gauss(AVG_ALL_RATINGS, STD_DEVIATION)
            predictions.append((eliteMovie[2], eliteMovie[3], prediction))

            if len(random_movies) == 0:
                break

            for randomMovie in random_movies:
                try:
                    predictions.append((randomMovie[2], randomMovie[3], random.uniform(0.5, 5)))
                    # predictions.append((randomMovie[1], randomMovie[2],random.gauss(AVG_ALL_RATINGS, STD_DEVIATION)))
                except KeyError:
                    continue

            # print sorted(predictions, key=lambda tup: tup[2], reverse=True)
            predictions_ids = [x[0] for x in sorted(predictions, key=lambda tup: tup[2], reverse=True)]
            eliteIndex = predictions_ids.index(eliteMovie[2])
            if eliteIndex <= N:
                hits += 1

        # print "Predictions for random", predictions
        # print hits, "hits", "out of", len(userMoviesTest)
        # exit()
        recall = hits / float(len(datasets['elite_test']))
        SumRecall += recall
        SumPrecision += (recall / float(N))
        SumMAE += evaluateMAE(conn, user, predictions)

    size = len(user_datasets)
    avgRecall = utils.evaluateAverage(SumRecall, size)
    avgPrecision = utils.evaluateAverage(SumPrecision, size)
    avgMae = utils.evaluateAverage(SumMAE, size)

    return avgPrecision, avgRecall, avgMae


def recommend(conn, Users, N, featureVector):

    # global DEEP_FEATURES, LOW_LEVEL_FEATURES

    SumRecall, SumPrecision, SumMAE = 0, 0, 1
    count = 0
    # test_list_size = 0

    for user in Users:
        # print "Training User", user[0], " model..."
        count += 1
        if count % 1000 == 0:
            print "1000 users evaluated"

        # select 70% of the users ratings for training

        # userBaseline = getUserBaseline(conn, user[0])
        userMoviesTraining, userMoviesTest = utils.getUserTrainingTestMovies(conn, user[0])
        # userInstances = utils.getUserInstances(userMovies, DEEP_FEATURES)
        # test = getEliteTestRatingSet(conn, user[0])

        if len(userMoviesTest) == 0:
            continue

        # test_list_size += len(userMoviesTest)

        userInstances, userValues = utils.getUserInstances(userMoviesTraining, featureVector)

        clf = svm.SVR(kernel='rbf')
        clf.fit(userInstances, userValues)
        # print len(userMoviesTest), "items in elite set."
        hits = 0
        # For each item rated high by the user
        for eliteMovie in userMoviesTest:
            predictions = []
            # print "Elite Movie", eliteMovie
            if eliteMovie[0] not in featureVector:
                continue

            prediction = clf.predict([featureVector[eliteMovie[0]]])
            predictions.append((eliteMovie[2], eliteMovie[3], prediction))

            randomMovies = utils.getRandomMovieSet(conn, user[0])

            for randomMovie in randomMovies:
                try:
                    prediction = clf.predict([featureVector[randomMovie[3]]])
                    predictions.append((randomMovie[1], randomMovie[2], prediction))
                except KeyError:
                    continue

            hits += count_hit(predictions, eliteMovie[2], N)

        # print hits, "hits", "out of", len(userMoviesTest)
        # exit()
        recall = hits / float(len(userMoviesTest))
        SumRecall += recall
        SumPrecision += (recall / float(N))
        # SumMAE += evaluateMAE(conn, user[0], predictions)

    # print "Average test size", (test_list_size / len(Users))

    size = len(Users)
    avgRecall = utils.evaluateAverage(SumRecall, size)
    avgPrecision = utils.evaluateAverage(SumPrecision, size)
    # avgMAE = utils.evaluateAverage(SumMAE, size)

    return avgPrecision, avgRecall, 1


def count_hit(predictions, eliteMovie, N):
    # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)
    predictions_ids = [x[0] for x in sorted(predictions, key=lambda tup: tup[2], reverse=True)]
    eliteIndex = predictions_ids.index(eliteMovie[2])
    # print "Elite Movie", eliteMovie, "Elite Index", eliteIndex
    # print "Elite Index", eliteIndex
    if eliteIndex <= N:
        return 1

    return 0



def predictUserRating(conn, userMovies, movieI, simFunction, userBaseline, feature_vector):

    global AVG_ALL_RATINGS

    SumSimilarityTimesRating = float(0)
    SumSimilarity = float(0)
    prediction = 0

    itemBaseline = utils.getItemBaseline(conn, userBaseline, movieI[2])  # check this ID index

    try:
        baselineUserItem = AVG_ALL_RATINGS + userBaseline + itemBaseline
    except TypeError:
        print "Type Error", userBaseline, "Movie Id", movieI[1]
        baselineUserItem = AVG_ALL_RATINGS + userBaseline

    AllSimilarities = [(movieJ, simFunction(movieI, movieJ, feature_vector)) for movieJ in userMovies]
    # AllSimilarities = [(movieJ, simFunction(movieI, movieJ, feature_vector), (float(movieJ[1] - baselineUserItem))) for movieJ in userMovies]
    # topSimilar = sorted(AllSimilarities, key=lambda tup: tup[1], reverse=True)[:30]

    # print userBaseline, itemBaseline

    # sims = [simFunction(movieI, movieJ, feature_vector) for movieJ in userMovies]
    # mult = [(movieJ[1] - baselineUserItem) for movieJ in userMovies]

    # numerator = sum([simFunction(movieI, movieJ, feature_vector) * (movieJ[1] - baselineUserItem) for movieJ in userMovies])
    # denominator = sum([simFunction(movieI, movieJ, feature_vector) for movieJ in userMovies])
    #
    # prediction = (numerator + denominator) + baselineUserItem

    # for movieJ, sim, mult in AllSimilarities:
    #     SumSimilarityTimesRating += (sim * mult)  # similarity * user rating
    #     SumSimilarity += abs(sim)



    for movieJ, sim in AllSimilarities:
        SumSimilarityTimesRating += (sim * (float(movieJ[1] - baselineUserItem)))  # similarity * user rating
        SumSimilarity += abs(sim)

    if (SumSimilarityTimesRating != 0 and SumSimilarity != 0):
        prediction = (SumSimilarityTimesRating / SumSimilarity) + baselineUserItem

    return prediction

# if __name__ == '__main__':
#     main()


def get_predict_collaborative_filtering(conn, eliteMovie, randomMovies, allMovies, userBaseline, feature_vector):

    predictions = []

    prediction = predictUserRating(conn, allMovies, eliteMovie, cosine, userBaseline, feature_vector)
    predictions.append((eliteMovie[2], eliteMovie[3], prediction))

    # print " Elite Movie", eliteMovie, prediction
    for randomMovie in randomMovies:
        try:
            prediction = predictUserRating(conn, allMovies, randomMovie, cosine, userBaseline, feature_vector)
            predictions.append((randomMovie[2], randomMovie[3], prediction))
        except KeyError:
            continue

    return predictions


def get_predict(eliteMovie, randomMovies, predictor_function, featureVector):

    predictions = []

    prediction = predictor_function([featureVector[eliteMovie[0]]])
    predictions.append((eliteMovie[2], eliteMovie[3], prediction))

    print "\nElite Predictions", predictions

    for randomMovie in randomMovies:
        try:
            prediction = predictor_function([featureVector[randomMovie[3]]])
            predictions.append((randomMovie[1], randomMovie[2], prediction))
        except KeyError:
            continue

    # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)

    return predictions