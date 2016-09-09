import constants
import random

def initializeLists():
    
    AVG_MAE = {"quanti": {"gower": 0, "cos-content": 0, "gower-features": 0, "cos-features": 0},
               "quali": {"gower": 0}, "both": {"gower": 0}, "triple": {"gower": 0, "cos-content": 0}}

    AVG_RECALL = {"quanti": {"gower": 0, "cos-content": 0, "gower-features": 0, "cos-features": 0},
               "quali": {"gower": 0}, "both": {"gower": 0}, "triple": {"gower": 0, "cos-content": 0}}

    return AVG_MAE, AVG_RECALL

def evaluateAverage(Sum, Count):
    Result = (Sum / Count)
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
    #Must have at least 200 ratings
    queryUsers = "SELECT u.userid FROM movielens_user u JOIN movielens_rating r ON r.userId = u.userId GROUP BY r.userId HAVING COUNT(r.movielensId) > 200"

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

    queryUserAverage = "SELECT SUM(rating)/COUNT(*) FROM movielens_rating WHERE userId = ?"

    c = constants.conn.cursor()
    c.execute(queryUserAverage, (user,))
    UserAverageRating = c.fetchone()

    return UserAverageRating
