# test the performance of different classifiers and regressors

import sqlite3
import utils
import recommender_classifier
import evaluation
from sklearn import svm
from datetime import datetime

t1 = datetime.now()

conn = sqlite3.connect('database.db')
Users = utils.selectRandomUsers(conn)

LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES = utils.extract_features()

SumRecall, SumPrecision, SumMAE = 0, 0, 0

t2 = datetime.now()

print (t2-t1).total_seconds()

def run(conn, Users, N, featureVector):

    SumRecall, SumPrecision, SumMAE = 0, 0, 1

    for user in Users:
        userMoviesTraining, userMoviesTest = utils.getUserTrainingTestMovies(conn, user[0])
        if len(userMoviesTest) == 0:
            continue

        userInstances, userValues = utils.getUserInstances(userMoviesTraining, featureVector)
        clf = svm.SVR(kernel='rbf')
        clf.fit(userInstances, userValues)
        hits = 0

        for eliteMovie in userMoviesTest:

            if eliteMovie[0] not in featureVector:
                continue

            predictions = get_predict(eliteMovie, user[0], clf.predict, featureVector)
            # print predictions
            hits += recommender_classifier.count_hit(predictions, eliteMovie, N)

        recall = hits / float(len(userMoviesTest))
        SumRecall += recall
        SumPrecision += (recall / float(N))
        # SumMAE += evaluation.evaluateMAE(conn, user[0], predictions)

    size = len(Users)
    avgRecall = utils.evaluateAverage(SumRecall, size)
    avgPrecision = utils.evaluateAverage(SumPrecision, size)
    avgMae = utils.evaluateAverage(SumMAE, size)

    return avgPrecision, avgRecall, avgMae


def get_predict(conn, eliteMovie, user, predictor_function, featureVector):

    predictions = []

    prediction = predictor_function([featureVector[eliteMovie[0]]])
    predictions.append((eliteMovie[2], eliteMovie[3], prediction))

    randomMovies = utils.getRandomMovieSet(conn, user)

    for randomMovie in randomMovies:
        try:
            prediction = predictor_function([featureVector[randomMovie[3]]])
            predictions.append((randomMovie[1], randomMovie[2], prediction))
        except KeyError:
            continue

    return predictions



precision, recall, mae = run(conn, Users, 5, LOW_LEVEL_FEATURES)
print "Low-Level Recall", recall, "Low-Level Precision", precision, "Low-Level MAE", mae, "For iteration with", 5

precision, recall, mae = run(conn, Users, 5, DEEP_FEATURES)
print "Deep Recall", recall, "Deep Precision", precision, "Deep MAE", mae, "For iteration with", 5

t2 = datetime.now()

print (t2-t1).total_seconds()