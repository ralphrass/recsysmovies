import sys
import constants
import string
import random
import utils
from utils import appendColumns, isValid, getValue
from evaluation import evaluateMAE, evaluateUserPrecisionRecall
from similarity import computeSimilarity, computeCosineSimilarityCollaborative, computeCosineSimilarityContent, computeGowerSimilarity

RECOMMENDATION_STRATEGY, SIMILARITY_MEASURE = "", ""
MIN, MAX = [], []
# REAL_RATINGS, PREDICTED_RATINGS = [], []
# AVERAGE_RANDOM_MAE = 0 #Control to execute only once

def loadMinMaxValues():
    if (not MIN) and (not MAX):
        for c in constants.COLUMNS:
            MIN.append(float(getValue('MIN', c, constants.conn)))
            MAX.append(float(getValue('MAX', c, constants.conn)))

def main(Users, SelectedMovies):

    # global REAL_RATINGS, PREDICTED_RATINGS, AVERAGE_RANDOM_MAE
    loadMinMaxValues()

    SumMAE, SumRecall, SumPrecision = 0, 0, 0
    #SumMAE = 0
    UsersPredictions = []

    for user in Users:
        # print "Computing for User ", user[0], "..."
        predictions = []
        #Predict rating for each movie
        for movieI in SelectedMovies:
            prediction = predictUserRating(user, movieI)
            predictions.append((movieI[constants.INDEX_COLUMN_ID], movieI[constants.INDEX_COLUMN_TITLE], prediction))

        topPredictions = sorted(predictions, key=lambda tup: tup[2], reverse=True)[:constants.PREDICTION_LIST_SIZE] # 2 is the index of the rating
        SumMAE += evaluateMAE(user[0], predictions) #predicted ratings for the same movies that the user rated
        recall, precision = evaluateUserPrecisionRecall(user[0], topPredictions)
        SumRecall += recall
        SumPrecision += precision

    return SumMAE, SumRecall, SumPrecision

def predictUserRating(user, movieI):

    # global SIMILARITY_MEASURE, REAL_RATINGS, RECOMMENDATION_STRATEGY, MIN, MAX
    global SIMILARITY_MEASURE, RECOMMENDATION_STRATEGY, MIN, MAX

    SumSimilarityTimesRating, SumSimilarity = float(0), float(0)
    prediction = 0
    # print "User ", user[0], " Movie ", movieI, " Value ", movieI[constants.INDEX_COLUMN_ID]
    c = constants.conn.cursor()
    c.execute(constants.getQueryUserMovies(), (user[0], movieI[constants.INDEX_COLUMN_ID],))

    for movieJ in c.fetchall():
        sim = computeSimilarity(SIMILARITY_MEASURE, movieI, movieJ, RECOMMENDATION_STRATEGY, MIN, MAX)
        SumSimilarityTimesRating += (sim * float(movieJ[constants.INDEX_COLUMN_RATING]))
        SumSimilarity += abs(sim)

    if (SumSimilarityTimesRating > 0 and SumSimilarity > 0):
        prediction = SumSimilarityTimesRating / SumSimilarity
        # REAL_RATINGS.append(movieJ[constants.INDEX_COLUMN_RATING])
        # PREDICTED_RATINGS.append(prediction)

    return prediction

if __name__ == '__main__':
    main()
