import sqlite3
import scipy
import numpy.linalg as LA
import numpy as np
from scipy.spatial.distance import cosine
import sys
from utils import appendColumns, isValid, getValue
import string
from sklearn.metrics import mean_absolute_error
import random

if len(sys.argv) < 3:
    print "Select Recommendation Strategy (Quantitative (quanti), Qualitative (quali), Both (both)) and Similarity Measure (Gower (gower), Cosine-Content (cos-content), Cosine-Collaborative (cos-collaborative))"
    sys.exit(0)

s, RECOMMENDATION_STRATEGY, SIMILARITY_MEASURE = sys.argv

conn = sqlite3.connect('database.db')
CURSOR_USERS = conn.cursor()
CURSOR_MOVIES = conn.cursor()
CURSOR_USERMOVIES = conn.cursor()
CURSOR_MOVIEI = conn.cursor()
CURSOR_MOVIEJ = conn.cursor()

SEPARATOR = ","

PREDICTION_LIST_SIZE = 20
RATING_THRESHOLD = 3

#This is used to select columns and to compute Gower similarity
COLUMNS = [
           "CAST(imdbrating AS REAL)",
           "CAST(tomatorating AS REAL)",
           #"movielensrating",
           "CAST(imdbvotes AS NUMERIC)",
           "CAST(year AS NUMERIC)",
           "CAST(metascore AS REAL)",
           "CAST(tomatouserrating AS REAL)"
           ]

COLUMNS_NOMINAL = [
            "genre",
            "actors",
            "director",
            "writer",
            "country",
            "language",
            "rated",
            "production"
            ]

NOMINAL_SPLIT = ["|", ", "]

MIN = []
MAX = []

# For Quantitative Columns Only
INDEX_COLUMN_ID = len(COLUMNS)
INDEX_COLUMN_TITLE = len(COLUMNS)+1
INDEX_COLUMN_RATING = len(COLUMNS)

REAL_RATINGS = []
PREDICTED_RATINGS = []

def appendQueryAllMovies():
    QUERY_ALL_MOVIES = ", mm.movielensId, m.title FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid LIMIT 1000"
    return QUERY_ALL_MOVIES

def appendQueryMovie():
    QUERY_MOVIE = ", r.rating, mm.movielensId, m.title FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid JOIN movielens_rating r ON r.movielensid = mm.movielensid WHERE r.userid = ? AND r.movielensId != ?"
    return QUERY_MOVIE

def loadMinMaxValues(conn):
    global COLUMNS

    for c in COLUMNS:
        MIN.append(float(getValue('MIN', c, conn)))
        MAX.append(float(getValue('MAX', c, conn)))

def recommendQuantitative():
    QUERY_ALL_MOVIES = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+appendQueryAllMovies()
    QUERY_MOVIE = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+appendQueryMovie()

    return QUERY_ALL_MOVIES, QUERY_MOVIE

def recommendQualitative():
    global INDEX_COLUMN_ID, INDEX_COLUMN_TITLE, INDEX_COLUMN_RATING

    QUERY_ALL_MOVIES = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryAllMovies()
    QUERY_MOVIE = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryMovie()

    INDEX_COLUMN_ID = len(COLUMNS_NOMINAL)
    INDEX_COLUMN_TITLE = len(COLUMNS_NOMINAL)+1
    INDEX_COLUMN_RATING = len(COLUMNS_NOMINAL)

    return QUERY_ALL_MOVIES, QUERY_MOVIE

def recommendBothStrategies():
    global INDEX_COLUMN_ID, INDEX_COLUMN_TITLE, INDEX_COLUMN_RATING

    QUERY_ALL_MOVIES = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+","+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryAllMovies()
    QUERY_MOVIE = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+","+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryMovie()

    INDEX_COLUMN_ID = len(COLUMNS)+len(COLUMNS_NOMINAL)
    INDEX_COLUMN_TITLE = len(COLUMNS)+len(COLUMNS_NOMINAL)+1
    INDEX_COLUMN_RATING = len(COLUMNS)+len(COLUMNS_NOMINAL)

    return QUERY_ALL_MOVIES, QUERY_MOVIE

def main():
    global conn

    loadMinMaxValues(conn)
    SumMAE, SumRandomMAE, CountUsers, UserAverageRating = 0, 0, 0, 0
    UsersPredictions, UsersRandomPredictions = [], []

    CURSOR_MOVIES.execute("SELECT movielensId FROM movielens_movie")
    AllMovies = CURSOR_MOVIES.fetchall()

    queryUserAverage = "SELECT SUM(rating)/COUNT(*) FROM movielens_rating WHERE userId = ?"

    query = "SELECT userid FROM movielens_user ORDER BY userid LIMIT 20" #WHERE userId = 26582" #138414 (202 avaliacoes)

    if (RECOMMENDATION_STRATEGY == "quanti"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendQuantitative()
    elif (RECOMMENDATION_STRATEGY == "quali"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendQualitative()
    elif (RECOMMENDATION_STRATEGY == "both"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendBothStrategies()

    for user in CURSOR_USERS.execute(query):

        print "Computing for User ", user[0], "..."

        CURSOR_USERMOVIES.execute(queryUserAverage, (user[0],))
        UserAverageRating = CURSOR_USERMOVIES.fetchone()

        predictions = []
        CountUsers += 1

        for movieI in CURSOR_MOVIES.execute(QUERY_ALL_MOVIES): #will predict rating to specified movies
            prediction = predictUserRating(QUERY_MOVIE, user, movieI)
            predictions.append((movieI[INDEX_COLUMN_ID], movieI[INDEX_COLUMN_TITLE], prediction))

        SumRandomMAE += evaluateRandomMAE(UserAverageRating)
        SumMAE += evaluateMAE()
        topPredictions = sorted(predictions, key=lambda tup: tup[2], reverse=True)[:PREDICTION_LIST_SIZE]
        #print topPredictions
        UsersPredictions.append((user[0],[a[0] for a in topPredictions])) #keep top predictions for each user (item id)
        UsersRandomPredictions.append((user[0], random.sample(AllMovies, PREDICTION_LIST_SIZE)))

    evaluate(SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions)
    conn.close()

def evaluate(SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions):
    print "MAE: ", (SumMAE / CountUsers)
    print "Random MAE: ", (SumRandomMAE / CountUsers)
    Precision, Recall, F1 = evaluatePrecisionRecallF1(UsersPredictions, CountUsers)
    RandomPrecision, RandomRecall, RandomF1 = evaluatePrecisionRecallF1(UsersRandomPredictions, CountUsers)
    print "Precision: ", Precision, " Recall: ", Recall, " F1: ", F1
    print "Random Precision: ", RandomPrecision, "Random Recall: ", RandomRecall, "Random F1: ", RandomF1

def predictUserRating(QUERY_MOVIE, user, movieI):

    global REAL_RATINGS, PREDICTED_RATINGS

    SumSimilarityTimesRating = float(0)
    SumSimilarity = float(0)
    prediction = 0 #TODO replace with baseline prediction

    #get all rated movies by current user (except the current movieI)
    for movieJ in CURSOR_USERMOVIES.execute(QUERY_MOVIE, (user[0], movieI[INDEX_COLUMN_ID])):

        if (SIMILARITY_MEASURE == 'gower'):
            sim = computeGowerSimilarity(movieI, movieJ)
        elif (SIMILARITY_MEASURE == 'cos-content'):
            sim = computeCosineSimilarityContent(movieI, movieJ)
        elif (SIMILARITY_MEASURE == 'cos-collaborative'):
            sim = computeCosineSimilarityCollaborative(movieI, movieJ)

        SumSimilarityTimesRating += (sim * movieJ[INDEX_COLUMN_RATING])
        SumSimilarity += abs(sim)

    if (SumSimilarityTimesRating > 0 and SumSimilarity > 0):
        prediction = SumSimilarityTimesRating / SumSimilarity
        REAL_RATINGS.append(movieJ[INDEX_COLUMN_RATING])
        PREDICTED_RATINGS.append(prediction)

    return prediction

def computeCosine(i, j):
    a = scipy.array(i)
    b = scipy.array(j)
    if (a.size == 0 and b.size == 0):
        return 0
    else:
        return cosine(a, b)

def computeCosineSimilarityCollaborative(i, j):
    movieIid = i[INDEX_COLUMN_ID]
    movieJid = j[INDEX_COLUMN_ID]

    CURSOR_MOVIEI.execute("SELECT rating FROM movielens_rating r WHERE r.movielensID = ? AND EXISTS (SELECT * FROM movielens_rating r2 WHERE r2.movielensID = ? AND r2.userId = r.userId)", (movieIid,movieJid,))
    CURSOR_MOVIEJ.execute("SELECT rating FROM movielens_rating r WHERE r.movielensID = ? AND EXISTS (SELECT * FROM movielens_rating r2 WHERE r2.movielensID = ? AND r2.userId = r.userId)", (movieJid,movieIid,))
    return computeCosine(CURSOR_MOVIEI.fetchall(), CURSOR_MOVIEJ.fetchall())

##TODO cosine qualitative
def computeCosineSimilarityContent(i, j):
    vI = []
    vJ = []

    if (RECOMMENDATION_STRATEGY == 'quanti'):
        for c in COLUMNS:
            iValue = float(i[COLUMNS.index(c)])
            jValue = float(j[COLUMNS.index(c)])
            if (isValid(iValue) and isValid(jValue)):
                vI.append(iValue)
                vJ.append(jValue)

    return computeCosine(vI, vJ)

def computeGowerQualitative(i, j):

    global RECOMMENDATION_STRATEGY

    SumSijk, SumDeltaijk, bothFactor = 0, 0, 0

    if (RECOMMENDATION_STRATEGY == 'both'):
        bothFactor = len(COLUMNS)

    for c in COLUMNS_NOMINAL:
        iValue = i[COLUMNS_NOMINAL.index(c)+bothFactor]
        jValue = j[COLUMNS_NOMINAL.index(c)+bothFactor]
        #print iValue, jValue
        if (isValid(iValue) and isValid(jValue)):
            if (c == "genre" or c == "actors"):
                values = iValue.split(NOMINAL_SPLIT[COLUMNS_NOMINAL.index(c)])
                for val in values:
                    if val in jValue:
                        SumSijk += 1
                        SumDeltaijk += 1
            else:
                if (iValue == jValue):
                    SumSijk += 1
                    SumDeltaijk += 1

    return SumSijk, SumDeltaijk

def computeGowerQuantitative(i, j):

    global MIN, MAX, COLUMNS

    SumSijk, SumDeltaijk = float(0), float(0)

    for c in COLUMNS:
        iValue = float(i[COLUMNS.index(c)])
        jValue = float(j[COLUMNS.index(c)])

        if (isValid(iValue) and isValid(jValue)):
            Deltaijk = 1
            diff = abs(iValue - jValue)
            Sijk = 1 - (diff / (MAX[COLUMNS.index(c)] - MIN[COLUMNS.index(c)]) )
        else:
            Sijk, Deltaijk = 0, 0

        SumDeltaijk += Deltaijk
        SumSijk += Sijk

    return SumSijk, SumDeltaijk

#TODO apply weights
# i and j are items (movies)
def computeGowerSimilarity(i, j):

    if (RECOMMENDATION_STRATEGY == 'quanti'):
        SumSijk, SumDeltaijk = computeGowerQuantitative(i, j)
    elif (RECOMMENDATION_STRATEGY == 'quali'):
        SumSijk, SumDeltaijk = computeGowerQualitative(i, j)
    else: #both
        a1,b1 = computeGowerQuantitative(i, j)
        a2,b2 = computeGowerQualitative(i, j)
        SumSijk, SumDeltaijk = (a1+a2), (b1+b2)

    if (SumDeltaijk == 0):
        return 0

    return (SumSijk / SumDeltaijk)

def evaluateMAE():
    global REAL_RATINGS, PREDICTED_RATINGS
    mae = mean_absolute_error(REAL_RATINGS, PREDICTED_RATINGS)
    return mae

def evaluateRandomMAE(UserAverageRating):
    global REAL_RATINGS
    randomMae = mean_absolute_error(REAL_RATINGS, [UserAverageRating]*len(REAL_RATINGS))
    return randomMae

def evaluatePrecisionRecallF1(UsersPredictions, CountUsers):
    global PREDICTION_LIST_SIZE, RATING_THRESHOLD, conn
    SumPrecision, SumRecall, SumF1 = 0, 0, 0

    queryRelevant = "SELECT movielensId FROM movielens_rating r WHERE r.userId = ? AND r.rating > ? ORDER BY rating DESC"

    for usersP in UsersPredictions:
        userId, userPredictions = usersP

        c = conn.cursor()
        c.execute(queryRelevant, (userId, RATING_THRESHOLD))
        topPredictions = [int(x[0]) for x in c.fetchall()[:PREDICTION_LIST_SIZE]]

        #True Positives: intersection between top recommended and positive evaluated by the user
        TP = float(len(list(set(topPredictions) & set(userPredictions))))
        FP = float(abs(PREDICTION_LIST_SIZE - TP)) #False Positives
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

if __name__ == '__main__':
    main()
