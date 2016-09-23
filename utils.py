import constants
import random
import sqlite3
import numpy as np
import io

def initializeLists():

    AVG_MAE = {"quanti": {"cos-content": 0, "cos-features": 0} }
    AVG_RECALL = {"quanti": {"cos-content": 0, "cos-features": 0} }
    AVG_PRECISION = {"quanti": {"cos-content": 0, "cos-features": 0} }


    # AVG_MAE = {"quanti": {"cos-content": 0, "cos-features": 0} }
               #"triple": {"cos-content": 0}}
    # AVG_RECALL = {"quanti": {"cos-content": 0, "cos-features": 0} }
               #"triple": {"cos-content": 0}}
    # AVG_PRECISION = {"quanti": {"cos-content": 0, "cos-features": 0} }
               #"triple": {"cos-content": 0}}

    # AVG_MAE = {"quanti": {"cos-content": 0, "cos-features": 0, "adjusted-cosine": 0} }
               #"triple": {"cos-content": 0}}
    # AVG_RECALL = {"quanti": {"cos-content": 0, "cos-features": 0, "adjusted-cosine": 0} }
               #"triple": {"cos-content": 0}}
    # AVG_PRECISION = {"quanti": {"cos-content": 0, "cos-features": 0, "adjusted-cosine": 0} }
               #"triple": {"cos-content": 0}}

    # AVG_MAE = {"quanti": {"gower": 0, "cos-content": 0, "gower-features": 0, "cos-features": 0},
    #            "quali": {"gower": 0}, "both": {"gower": 0}, "triple": {"gower": 0, "cos-content": 0}}
    # AVG_PRECISION = {"quanti": {"gower": 0, "cos-content": 0, "gower-features": 0, "cos-features": 0},
    #            "quali": {"gower": 0}, "both": {"gower": 0}, "triple": {"gower": 0, "cos-content": 0}}
    # AVG_RECALL = {"quanti": {"gower": 0, "cos-content": 0, "gower-features": 0, "cos-features": 0},
    #            "quali": {"gower": 0}, "both": {"gower": 0}, "triple": {"gower": 0, "cos-content": 0}}

    return AVG_MAE, AVG_RECALL, AVG_PRECISION

def evaluateAverage(Sum, Count):
    Result = (Sum / float(Count))
    return Result

def appendColumns(columns):
    columnList = []
    for c in columns:
        columnList.append(c)
    return columnList

def isValid(item):
    return (item != 'N/A' and (not (not item))) #Do not contain invalid and is not empty

def getValue(function, attribute, conn):

    CURSOR_VALUE = conn.cursor()

    if (function == 'MIN'):
        function = "MAX(MIN("+attribute+"), 0)"
    else:
        function = "MAX("+attribute+")"
    query = "SELECT "+function+" FROM movies WHERE "+attribute+" != 'N/A'"
    #print query
    CURSOR_VALUE.execute(query)
    return CURSOR_VALUE.fetchone()[0]

def loadMinMaxValues(conn, COLUMNS):
    for c in COLUMNS:
        MIN.append(float(getValue('MIN', c, conn)))
        MAX.append(float(getValue('MAX', c, conn)))

def selectRandomUsers():
    # Must have at least 200 ratings and used tags
    queryUsers = "SELECT u.userid FROM movielens_user_with_tags u JOIN movielens_rating r ON r.userId = u.userId GROUP BY r.userId HAVING COUNT(r.movielensId) > 200"

    c = constants.conn.cursor()
    c.execute(queryUsers)
    Users = random.sample(c.fetchall(), constants.NUM_USERS) #Users for this iteration

    return Users

def selectRandomMovies():

    QUERY_ALL_MOVIES = constants.getQueryAllMovies()

    c = constants.conn.cursor()
    c.execute(QUERY_ALL_MOVIES)
    SelectedMovies = random.sample(c.fetchall(), constants.LIMIT_ITEMS_TO_PREDICT)

    return SelectedMovies

def getUserAverageRating(user):

    # queryUserAverage = "SELECT SUM(rating)/COUNT(*) FROM movielens_rating WHERE userId = ?"
    queryUserAverage = "SELECT avgrating FROM movielens_user WHERE userId = ?"

    c = constants.conn.cursor()
    c.execute(queryUserAverage, (user,))
    UserAverageRating = float(c.fetchone()[0])
    
    return UserAverageRating


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
