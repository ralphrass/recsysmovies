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


def collaborative(movieI, movieJ, conn):

    # select all the ratings of movie I from users that also rated movie J
    ratingsI = np.array([x[0] for x in utils.getMovieRatings1(conn, movieI[2], movieJ[2])])
    ratingsJ = np.array([x[0] for x in utils.getMovieRatings2(conn, movieI[2], movieJ[2])])

    if len(ratingsI) > 0 and len(ratingsJ) > 0:
        return cosine_similarity([ratingsI], [ratingsJ])
    return 0


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


def cosine_tfidf(userid, movielensid, user_feature_vector, movie_feature_vector):

    user_profile = user_feature_vector[userid]
    movie_profile = movie_feature_vector[movielensid]

    try:
        cos = cosine_similarity([user_profile], [movie_profile])
        sim = cos[0][0]
    except ValueError:
        print "Value Error on user", userid, "and/or movie", movielensid
        sim = 0
    return sim


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


def recommend_random(user_profiles, N):

    global AVG_ALL_RATINGS, STD_DEVIATION

    conn = sqlite3.connect('database.db')

    SumRecall, SumPrecision, SumMAE = 0, 0, 0

    for user in user_profiles.iteritems():
        # print "Training User", user[0], " model..."
        datasets = user[1]['datasets']

        if len(datasets['elite_test']) == 0:
            continue

        predictions = []
        # useravg = utils.getUserAverageRating(conn, user[0])

        random_movies = datasets['random']

        hits = 0

        for movie in random_movies:
            prediction = random.uniform(0.5, 5)
            predictions.append((movie[2], movie[3], prediction))

        # For each item rated high by the user
        for eliteMovie in datasets['elite_test']:
            prediction = random.uniform(0.5, 5)
            # print "Elite Movie", eliteMovie, prediction
            if len(random_movies) == 0:
                break

            current_predictions = predictions[:]
            current_predictions.append((eliteMovie[2], eliteMovie[3], prediction))

            # print sorted(predictions, key=lambda tup: tup[2], reverse=True)
            predictions_ids = [x[0] for x in sorted(current_predictions, key=lambda tup: tup[2], reverse=True)]
            eliteIndex = predictions_ids.index(eliteMovie[2])
            # print eliteMovie, eliteIndex
            if eliteIndex < N:
                hits += 1

            # print "Predictions for random", sorted(current_predictions, key=lambda t: t[2], reverse=True)
        # print hits, "hits", "out of", len(userMoviesTest)
        # exit()
        recall = hits / float(len(datasets['elite_test']))
        SumRecall += recall
        SumPrecision += (recall / float(N))
        SumMAE += evaluateMAE(conn, user[0], predictions)

    size = len(user_profiles)
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
    if eliteIndex < N:
        return 1

    return 0


def predictUserRating(conn, user_profile, movieI, feature_vector, feature_vector2=None):

    global AVG_ALL_RATINGS

    all_movies = user_profile['datasets']['all_movies']
    user_baseline = user_profile['baseline']

    numerator, denominator = float(0), float(0)
    prediction = 0

    itemBaseline = utils.getItemBaseline(conn, user_baseline, movieI[2])  # check this ID index

    try:
        baselineUserItem = AVG_ALL_RATINGS + user_baseline + itemBaseline
    except TypeError:
        print "Type Error", user_baseline, "Movie Id", movieI[1]
        baselineUserItem = AVG_ALL_RATINGS + user_baseline

    if feature_vector2 is None:
        AllSimilarities = [(movieJ, cosine(movieI, movieJ, feature_vector)) for movieJ in all_movies]
    else:
        AllSimilarities = [(movieJ, cosine_tfidf(user_profile['userid'], movieJ[2], feature_vector, feature_vector2)) for movieJ in all_movies]
    # print "Current Movie", movieI
    # print "Top Similar", sorted(AllSimilarities, key=lambda tup: tup[1], reverse=True)[:30]

    for movieJ, sim in AllSimilarities:
        # numerator += (sim * (float(movieJ[1] - baselineUserItem)))  # similarity * user rating
        if sim > 0:
            numerator += (sim * (float(movieJ[1])))
            denominator += abs(sim)

    if (numerator != 0 and denominator != 0):
        # prediction = (numerator / denominator) + baselineUserItem
        prediction = (numerator / denominator) + baselineUserItem

    # print "Numerator", numerator
    # print "Denominator", denominator
    # print "Baseline", baselineUserItem
    # print "Prediction", prediction

    return prediction


def get_prediction_elite(conn, elite_movie, user_profile, feature_vector, feature_vector2=None):

    # if feature_vector is None:
    #     sim_function = collaborative
    # else:
    #     sim_function = cosine

    prediction = predictUserRating(conn, user_profile, elite_movie, feature_vector, feature_vector2)
    # print "Elite Prediction", (elite_movie[2], elite_movie[3], prediction)

    return (elite_movie[2], elite_movie[3], prediction)


def get_predict_collaborative_filtering(conn, user_profile, feature_vector, feature_vector2=None):

    # if feature_vector is None:
    #     sim_function = collaborative
    # else:
    #     sim_function = cosine

    predictions = []

    for random_movie in user_profile['datasets']['random']:
        # print "Prediction for ", random_movie
        try:
            prediction = predictUserRating(conn, user_profile, random_movie, feature_vector, feature_vector2)
            predictions.append((random_movie[2], random_movie[3], prediction))
            # print prediction
        except KeyError:
            continue

    # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)
    return predictions


def get_predict(eliteMovie, randomMovies, predictor_function, featureVector):

    predictions = []

    prediction = predictor_function([featureVector[eliteMovie[0]]])
    predictions.append((eliteMovie[2], eliteMovie[3], prediction))

    # print "\nElite Predictions", predictions

    for randomMovie in randomMovies:
        try:
            prediction = predictor_function([featureVector[randomMovie[3]]])
            predictions.append((randomMovie[1], randomMovie[2], prediction))
        except KeyError:
            continue

    # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)

    return predictions


def build_user_profiles(conn, Users):

    user_profiles = {}

    for user in Users:

        # print user[0]

        userMoviesTraining, userMoviesTest, full_test_set, all_movies = utils.getUserTrainingTestMovies(conn, user[0])

        if len(userMoviesTest) == 0:
            continue

        random_movies = utils.getRandomMovieSet(conn, user[0])
        user_baseline = utils.getUserBaseline(conn, user[0])

        user_profiles[user[0]] = {'datasets': {'all_movies': all_movies, 'train': userMoviesTraining,
                                               'elite_test': userMoviesTest,
                                  'test': full_test_set, 'random': random_movies},
                                  'baseline': user_baseline, 'userid': user[0]}
    return user_profiles
