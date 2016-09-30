from sklearn.metrics import mean_absolute_error
# import constants
import utils
import random
import numpy as np
import string

RATING_THRESHOLD = 3


def evaluateAverageMAE(SumMAE, CountUsers):
    MAE = (SumMAE / CountUsers)
    return MAE


# predictions is a list of tuples which contains: MovieLensId, MovieTitle, PredictedRating
def evaluateMAE(conn, user, predictions, movielensid_index=0, rating_index=2):
    predictedRatings, realRatings = [], []

    query = "SELECT rating FROM movielens_rating WHERE userId = ? AND movielensId = ?"

    # print "Full Predictions", predictions

    # will search for intersections
    for prediction in predictions:
        c = conn.cursor()
        c.execute(query, (user, prediction[movielensid_index],))
        result = c.fetchone()

        if (type(result) is tuple):
            predictedRatings.append(prediction[rating_index])
            realRatings.append(float(result[0]))

    # print "Predictions"
    # print len(predictions)
    # print "Real Ratings"
    # print len(realRatings)

    if len(predictedRatings) != 0:
        return mean_absolute_error(realRatings, predictedRatings)

    return 0


def evaluateRandomMAE(conn, Users, Items, useUserAverageRating=True):
    queryUserMovies = "SELECT rating FROM movielens_rating WHERE userId = ? AND movielensid = ?"
    SumRandomMAE = 0
    userPredictions = []

    for user in Users:

        if useUserAverageRating:
            UserAverageRating = Users[1]
            # UserAverageRating = utils.getUserAverageRating(user[0])

        REAL_RATINGS = []

        for item in Items:

            c = conn.cursor()
            c.execute(queryUserMovies, (user[0], item[0],))
            result = c.fetchone()
            if (type(result) is tuple):
                REAL_RATINGS.append(result[0])

        if len(REAL_RATINGS) != 0:
            if useUserAverageRating:
                try:
                    userPredictions = [UserAverageRating] * len(REAL_RATINGS)
                except IndexError:
                    print "Index Error", UserAverageRating, REAL_RATINGS
            else:
                userPredictions = np.random.uniform(0.5, 5, len(REAL_RATINGS))

            try:
                randomMae = mean_absolute_error(REAL_RATINGS, userPredictions)
                SumRandomMAE += randomMae
            except ValueError:
                print REAL_RATINGS, userPredictions

    return (SumRandomMAE / len(Users))


def evaluateRandomPrecisionRecall(conn, Users, Items, PREDICTION_LIST_SIZE, LIMIT_ITEMS_TO_PREDICT):
    global RATING_THRESHOLD

    SumRecall, SumPrecision = 0, 0
    queryRelevant = "SELECT movielensId FROM movielens_rating r WHERE r.userId = ? AND r.rating > ? ORDER BY rating DESC LIMIT ?"
    ItemsIds = [movie[0] for movie in Items]

    strItemsIds = ",".join("?" * len(ItemsIds))

    for user in Users:
        queryUserMovies = "SELECT movielensid FROM movielens_rating WHERE userId = " + str(
            user[0]) + " AND movielensid IN (" + strItemsIds + ") LIMIT "+str(PREDICTION_LIST_SIZE)

        c = conn.cursor()
        userMovies = c.execute(queryUserMovies, ItemsIds).fetchall()
        predictionsIds = [int(x[0]) for x in userMovies]
        if len(predictionsIds) != 0:

            # all movies that are relevant for this user
            c = conn.cursor()
            c.execute(queryRelevant, (user[0], RATING_THRESHOLD, LIMIT_ITEMS_TO_PREDICT))
            RelevantMovies = [int(x[0]) for x in c.fetchall()]

            # True Positives: intersection between top recommended and positive evaluated by the user
            TP = float(len(list(set(RelevantMovies) & set(predictionsIds))))
            FP = float(abs(PREDICTION_LIST_SIZE - TP))  # False Positives
            FN = float(abs(len(RelevantMovies) - TP))  # False Negatives
            # print "User", user[0]
            # print "Relevant", topRelevant
            # print "Predictions", predictionsIds
            # print "TP: ", TP, " FP: ", FP, " FN: ", FN
            try:
                Recall = TP / (TP + FN)
                Precision = TP / (TP + FP)
                SumRecall += Recall
                SumPrecision += Precision
            except ZeroDivisionError:
                return 0, 0
                continue

                # print "SUM Recall", SumRecall, "SUM Precision", SumPrecision

    AvgPrecision = SumPrecision / len(Users)
    AvgRecall = SumRecall / len(Users)

    return AvgRecall, AvgPrecision


# def evaluateUserPrecisionRecall(user, userPredictions):
def evaluateUserPrecisionRecall(conn, user, predictions, PREDICTION_LIST_SIZE):

    global RATING_THRESHOLD

    queryRelevant = "SELECT movielensId, rating FROM movielens_rating r WHERE r.userId = ? AND r.rating > ? ORDER BY rating DESC"

    # predictedPredictions = [int(x[0]) for x in userPredictions]

    c = conn.cursor()
    c.execute(queryRelevant, (user, RATING_THRESHOLD,))  # all movies that are relevant for this user
    RelevantMovies = c.fetchall()
    topPredictions = [int(x[0]) for x in RelevantMovies[:PREDICTION_LIST_SIZE]]
    print "User ", user
    print "User Relevant Movies", topPredictions
    print "User Predictions ", predictions
    print "Intersection ", list(set(topPredictions) & set(predictions))

    # True Positives: intersection between top recommended and positive evaluated by the user
    TP = float(len(list(set(topPredictions) & set(predictions))))
    FP = float(abs(PREDICTION_LIST_SIZE - TP))  # False Positives
    FN = float(abs(len(RelevantMovies) - TP))  # False Negatives

    # print "Relevant", topPredictions
    # print "Predictions", predictions
    print "TP: ", TP, " FP: ", FP, " FN: ", FN

    try:
        Recall = TP / (TP + FN)
        Precision = TP / (TP + FP)
        return Recall, Precision
    except ZeroDivisionError:
        return 0, 0
