import sqlite3
import sys
import constants
import string
import random
from utils import appendColumns, isValid, getValue
from evaluation import evaluate, evaluateMAE, evaluateRandomMAE, evaluatePrecisionRecallF1
from similarity import computeSimilarity, computeCosineSimilarityCollaborative, computeCosineSimilarityContent, computeGowerSimilarity

# if len(sys.argv) < 3:
#     print "Select Recommendation Strategy (Quantitative (quanti), Qualitative (quali), Both (both)) and Similarity Measure (Gower (gower), Cosine-Content (cos-content), Cosine-Collaborative (cos-collaborative))"
#     sys.exit(0)
#
# s, RECOMMENDATION_STRATEGY, SIMILARITY_MEASURE = sys.argv

RECOMMENDATION_STRATEGY, SIMILARITY_MEASURE = "", ""
MIN, MAX = [], []
REAL_RATINGS, PREDICTED_RATINGS = [], []
AVERAGE_RANDOM_MAE = 0 #Control to execute only once

def loadMinMaxValues():
    if (not MIN) and (not MAX):
        for c in constants.COLUMNS:
            MIN.append(float(getValue('MIN', c, constants.conn)))
            MAX.append(float(getValue('MAX', c, constants.conn)))

def main():

    global REAL_RATINGS, PREDICTED_RATINGS, AVERAGE_RANDOM_MAE

    REAL_RATINGS, PREDICTED_RATINGS = [], []

    loadMinMaxValues()

    SumMAE, SumRandomMAE, CountUsers, UserAverageRating = 0, 0, 0, 0
    UsersPredictions, UsersRandomPredictions = [], []

    constants.CURSOR_MOVIES.execute("SELECT movielensId FROM movielens_movie")
    AllMovies = constants.CURSOR_MOVIES.fetchall()

    queryUserAverage = "SELECT SUM(rating)/COUNT(*) FROM movielens_rating WHERE userId = ?"
    # query = "SELECT userid FROM movielens_user ORDER BY userid LIMIT ?" #WHERE userId = 26582" #138414 (202 avaliacoes)
    # User rated at least 50 movies
    # query = "SELECT u.userid FROM movielens_user u JOIN movielens_rating r ON r.userId = u.userId GROUP BY r.userId HAVING COUNT(r.movielensId) > 100 LIMIT ?"
    query = "SELECT u.userid FROM movielens_user u"

    QUERY_ALL_MOVIES, QUERY_MOVIE = constants.setQueries(RECOMMENDATION_STRATEGY)

    AllUsers = constants.CURSOR_USERS.execute(query)
    Users = random.sample(AllMovies, constants.NUM_USERS)

    # for user in constants.CURSOR_USERS.execute(query, (constants.NUM_USERS,)):
    for user in Users:
        # print "Computing for User ", user[0], "..."
        predictions = []
        CountUsers += 1

        c = constants.conn.cursor()
        c.execute(QUERY_ALL_MOVIES)
        AllMovies = c.fetchall()
        SelectedMovies = random.sample(AllMovies, constants.LIMIT_ITEMS_TO_PREDICT)

        # for movieI in constants.CURSOR_MOVIES.execute(QUERY_ALL_MOVIES, (constants.LIMIT_ITEMS_TO_PREDICT,)): #will predict rating to specified movies
        for movieI in SelectedMovies:
            prediction = predictUserRating(QUERY_MOVIE, user, movieI)
            predictions.append((movieI[constants.INDEX_COLUMN_ID], movieI[constants.INDEX_COLUMN_TITLE], prediction))

        if AVERAGE_RANDOM_MAE == 0:
            c2 = constants.conn.cursor()
            c2.execute(queryUserAverage, (user[0],))
            UserAverageRating = c2.fetchone()
            SumRandomMAE += evaluateRandomMAE(REAL_RATINGS, UserAverageRating)
            UsersRandomPredictions.append((user[0], random.sample(AllMovies, constants.PREDICTION_LIST_SIZE)))

        SumMAE += evaluateMAE(REAL_RATINGS, PREDICTED_RATINGS)
        topPredictions = sorted(predictions, key=lambda tup: tup[2], reverse=True)[:constants.PREDICTION_LIST_SIZE] # 2 is the index of the rating
        #print topPredictions
        UsersPredictions.append((user[0],[a[0] for a in topPredictions])) #keep top predictions for each user (item id)


    return SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions
    # evaluate(SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions)
    # constants.conn.close()

def predictUserRating(QUERY_MOVIE, user, movieI):

    global SIMILARITY_MEASURE, REAL_RATINGS, PREDICTED_RATINGS, RECOMMENDATION_STRATEGY, MIN, MAX

    SumSimilarityTimesRating = float(0)
    SumSimilarity = float(0)
    prediction = 0

    # print QUERY_MOVIE
    # print "User ", user[0], " Movie ", movieI, " Value ", movieI[constants.INDEX_COLUMN_ID]

    c3 = constants.conn.cursor()

    try:
        c3.execute(QUERY_MOVIE, (user[0], movieI[constants.INDEX_COLUMN_ID],))
    except IndexError:
        print QUERY_MOVIE
        print user[0]
        print movieI
        print constants.INDEX_COLUMN_ID

    AllUserMovies = c3.fetchall()

    try:
        limit = constants.LIMIT_ITEMS_TO_COMPARE
        if len(AllUserMovies) < limit:
            limit = len(AllUserMovies)
        SelectedUserMovies = random.sample(AllUserMovies, limit)
    except ValueError:
        print "query", QUERY_MOVIE
        print "User ", user[0]

    #get all rated movies by current user (except the current movieI)
    # for movieJ in constants.CURSOR_USERMOVIES.execute(QUERY_MOVIE, (user[0], movieI[constants.INDEX_COLUMN_ID], constants.LIMIT_ITEMS_TO_COMPARE)):
    for movieJ in SelectedUserMovies:

        sim = computeSimilarity(SIMILARITY_MEASURE, movieI, movieJ, RECOMMENDATION_STRATEGY, MIN, MAX)

        SumSimilarityTimesRating += (sim * float(movieJ[constants.INDEX_COLUMN_RATING]))
        SumSimilarity += abs(sim)

    if (SumSimilarityTimesRating > 0 and SumSimilarity > 0):
        prediction = SumSimilarityTimesRating / SumSimilarity
        REAL_RATINGS.append(movieJ[constants.INDEX_COLUMN_RATING])
        PREDICTED_RATINGS.append(prediction)

    return prediction

if __name__ == '__main__':
    main()
