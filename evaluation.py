from sklearn.metrics import mean_absolute_error
import constants

RATING_THRESHOLD = 3

def evaluateAverageMAE(SumMAE, CountUsers, SumRandomMAE):

    MAE = (SumMAE / CountUsers)

    if SumRandomMAE > 0:
        RandomMAE = (SumRandomMAE / CountUsers)
    else:
        RandomMAE = 0

    return MAE, RandomMAE

def evaluate(SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions):

    MAE, RandomMAE = evaluateAverageMAE(SumMAE, CountUsers, SumRandomMAE)

    print "MAE: ", MAE
    print "Random MAE: ", RandomMAE
    Precision, Recall, F1 = evaluatePrecisionRecallF1(UsersPredictions, CountUsers)
    RandomPrecision, RandomRecall, RandomF1 = evaluatePrecisionRecallF1(UsersRandomPredictions, CountUsers)
    print "Precision: ", Precision, " Recall: ", Recall, " F1: ", F1
    print "Random Precision: ", RandomPrecision, "Random Recall: ", RandomRecall, "Random F1: ", RandomF1

    return MAE, RandomMAE, Precision, Recall, F1, RandomPrecision, RandomRecall, RandomF1

def evaluateMAE(REAL_RATINGS, PREDICTED_RATINGS):

    if len(PREDICTED_RATINGS) != 0:
        mae = mean_absolute_error(REAL_RATINGS, PREDICTED_RATINGS)
    else:
        mae = 0

    return mae

def evaluateRandomMAE(REAL_RATINGS, UserAverageRating):

    if len(REAL_RATINGS) != 0:
        randomMae = mean_absolute_error(REAL_RATINGS, [UserAverageRating]*len(REAL_RATINGS))
    else:
        randomMae = 0
        
    return randomMae

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

        # print "TP: ", TP, " FP: ", FP, " FN: ", FN

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
