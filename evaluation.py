from sklearn.metrics import mean_absolute_error
import constants
import utils
import random
import numpy as np

RATING_THRESHOLD = 3

def evaluateAverageMAE(SumMAE, CountUsers):
    MAE = (SumMAE / CountUsers)
    return MAE

# predictions is a list of tuples which contains: MovieLensId, MovieTitle, PredictedRating
def evaluateMAE(user, predictions):

    predictedRatings, realRatings = [], []

    query = "SELECT rating FROM movielens_rating WHERE userId = ? AND movielensId = ?"

    #will search for intersections
    for prediction in predictions:
        c = constants.conn.cursor()
        c.execute(query, (user, prediction[0],))
        result = c.fetchone()

        if (type(result) is tuple):
             predictedRatings.append(prediction[2])
             realRatings.append(float(result[0]))

    if len(predictedRatings) != 0:
        return mean_absolute_error(realRatings, predictedRatings)

    return 0

def evaluateRandomMAE(Users, Items, useUserAverageRating=True):

    queryUserMovies = "SELECT rating FROM movielens_rating WHERE userId = ? AND movielensid = ?"
    SumRandomMAE = 0

    for user in Users:

        if useUserAverageRating:
            UserAverageRating = utils.getUserAverageRating(user[0])

        REAL_RATINGS = []

        for item in Items:

            c = constants.conn.cursor()
            c.execute(queryUserMovies, (user[0],item[constants.INDEX_COLUMN_ID],))
            result = c.fetchone()

            if (type(result) is tuple):
                REAL_RATINGS.append(result[0])

        if len(REAL_RATINGS) != 0:
            if useUserAverageRating:
                randomMae = mean_absolute_error(REAL_RATINGS, [UserAverageRating]*len(REAL_RATINGS))
            else:
                randomMae = mean_absolute_error(REAL_RATINGS, np.random.uniform(0.5, 5, len(REAL_RATINGS)))
            SumRandomMAE += randomMae

    return (SumRandomMAE / len(Users))

def evaluateUserPrecisionRecall(user, userPredictions):

    RATING_THRESHOLD, SumRecall = 3, 0
    queryRelevant = "SELECT movielensId FROM movielens_rating r WHERE r.userId = ? AND r.rating > ? ORDER BY rating DESC"

    predictedPredictions = [int(x[0]) for x in userPredictions]

    c = constants.conn.cursor()
    c.execute(queryRelevant, (user, RATING_THRESHOLD,)) #all movies that are relevant for this user
    RelevantMovies = c.fetchall()
    topPredictions = [int(x[0]) for x in RelevantMovies[:constants.PREDICTION_LIST_SIZE]]

    #True Positives: intersection between top recommended and positive evaluated by the user
    TP = float(len(list(set(topPredictions) & set(predictedPredictions))))
    FP = float(abs(constants.PREDICTION_LIST_SIZE - TP)) #False Positives
    FN = float(abs(len(RelevantMovies) - TP)) #False Negatives

    try:
        Recall = TP / (TP+FN)
        Precision = TP / (TP+FP)
        return Recall, Precision
    except ZeroDivisionError:
        return 0, 0

def evaluatePrecisionRecallF1(UsersPredictions, CountUsers):
    global RATING_THRESHOLD

    SumPrecision, SumRecall, SumF1 = 0, 0, 0

    queryRelevant = "SELECT movielensId FROM movielens_rating r WHERE r.userId = ? AND r.rating > ? ORDER BY rating DESC"

    for usersP in UsersPredictions:
        userId, userPredictions = usersP

        c = constants.conn.cursor()
        c.execute(queryRelevant, (userId, RATING_THRESHOLD))
        topPredictions = [int(x[0]) for x in c.fetchall()[:constants.PREDICTION_LIST_SIZE]]

        #True Positives: intersection between top recommended and positive evaluated by the user
        TP = float(len(list(set(topPredictions) & set(userPredictions))))
        FP = float(abs(constants.PREDICTION_LIST_SIZE - TP)) #False Positives
        FN = float(abs(len(c.fetchall()) - TP)) #False Negatives

        print "TP: ", TP, " FP: ", FP, " FN: ", FN

        try:
            Precision = TP / (TP+FP)
        except ZeroDivisionError:
            Precision = 0

        try:
            Recall = TP / (TP+FN)
        except ZeroDivisionError:
            Recall = 0

        try:
            F1 = (2*Precision*Recall) / (Precision + Recall)
        except ZeroDivisionError:
            F1 = 0

        SumPrecision += Precision
        SumRecall += Recall
        SumF1 += F1

    AvgPrecision = SumPrecision / CountUsers
    AvgRecall = SumRecall / CountUsers
    AvgF1 = SumF1 / CountUsers

    return AvgPrecision, AvgRecall, AvgF1
