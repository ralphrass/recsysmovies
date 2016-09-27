import io
import numpy as np
import random
import sqlite3

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

# def loadMinMaxValues(conn, COLUMNS):
#     for c in COLUMNS:
#         MIN.append(float(getValue('MIN', c, conn)))
#         MAX.append(float(getValue('MAX', c, conn)))

def selectRandomUsers(conn, limit):
    # Must have at least 200 ratings and used tags
    queryUsers = "SELECT u.userid, u.avgrating " \
                 "FROM movielens_user u " \
                 "JOIN movielens_rating r ON r.userId = u.userId " \
                 "JOIN movielens_movie m ON m.movielensid = r.movielensid " \
                 "JOIN trailers t ON t.imdbid = m.imdbidtt " \
                 "WHERE t.best_file = 1 " \
                 "GROUP BY r.userId HAVING COUNT(r.movielensId) > 200"

    c = conn.cursor()
    c.execute(queryUsers)
    Users = random.sample(c.fetchall(), limit) #Users for this iteration
    # Users = c.fetchall()

    return Users

def selectTrainingMovies(conn):

    query = "SELECT 1, mm.movielensId, m.title, t.id " \
            "FROM movies m " \
            "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
            "JOIN trailers t ON t.imdbID = m.imdbID " \
            "AND t.best_file = 1 " \
            # "AND CAST(imdbvotes AS NUMERIC) > 5"

    c = conn.cursor()
    c.execute(query)
    # SelectedMovies = random.sample(c.fetchall(), limit)
    SelectedMovies = c.fetchall()

    return SelectedMovies

def getUserMovies(conn, user):
    sql = "SELECT r.rating, mm.movielensId, m.title, t.id " \
          "FROM movies m " \
          "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
          "JOIN movielens_rating r ON r.movielensid = mm.movielensid " \
          "JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 " \
          "WHERE r.userid = ? "
    # print sql, user
    c = conn.cursor()
    c.execute(sql, (user,))
    return c.fetchall()

# Equal to 5 stars ==> [Greater than 4 stars]
def getEliteTestRatingSet(conn, user):
    sql = "SELECT m.rating , m.movielensid, mm.title, t.id " \
          "FROM movielens_rating_elite m " \
          "JOIN movielens_movie mm ON mm.movielensid = m.movielensid " \
          "JOIN trailers t ON t.imdbID = mm.imdbIDtt " \
          "AND t.best_file = 1 " \
          "WHERE userid = ?"

    c = conn.cursor()
    c.execute(sql, (user,))
    return c.fetchall()

# Randomly select items unrated by the user
def getRandomMovieSet(conn, user):
    sql = "SELECT 1, mm.movielensId, m.title, t.id " \
          "FROM movies m " \
          "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
          "JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 " \
          "EXCEPT " \
          "SELECT 1, mm.movielensId, m.title, t.id " \
          "FROM movies m " \
          "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
          "JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 " \
          "JOIN movielens_rating r ON r.movielensid = mm.movielensid " \
          "WHERE r.userid = ? "
    # print sql, user
    limit = 100
    c = conn.cursor()
    c.execute(sql, (user,))
    Movies = random.sample(c.fetchall(), limit)
    # print Movies

    return Movies

def getUserBaseline(conn, user):
    sql = "SELECT SUM(rating - 3.5161)/COUNT(rating) " \
          "FROM movielens_rating " \
          "WHERE userid = ?"
    # print sql, user
    c = conn.cursor()
    c.execute(sql, (user,))
    return c.fetchone()[0]

def getItemBaseline(conn, userbaseline, movie):
    sql = "SELECT SUM(rating - ? - 3.5161)/COUNT(rating) " \
          "FROM movielens_rating " \
          "WHERE movielensid = ?"
    # print sql, userbaseline, movie
    c = conn.cursor()
    c.execute(sql, (userbaseline, movie,))
    return c.fetchone()[0]


def getUserAverageRating(conn, user):

    # queryUserAverage = "SELECT SUM(rating)/COUNT(*) FROM movielens_rating WHERE userId = ?"
    queryUserAverage = "SELECT avgrating FROM movielens_user WHERE userId = ?"

    c = conn.cursor()
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
