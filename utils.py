import io
import numpy as np
import random
import sqlite3


def evaluateAverage(Sum, Count):
    try:
        Result = (Sum / float(Count))
    except ZeroDivisionError:
        return 0
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


def selectRandomUsers(conn):
    # Must have at least 200 ratings and used tags
    queryUsers = "SELECT u.userid, u.avgrating " \
                 "FROM movielens_user u " \
                 "JOIN movielens_rating r ON r.userId = u.userId " \
                 "JOIN movielens_movie m ON m.movielensid = r.movielensid " \
                 "JOIN trailers t ON t.imdbid = m.imdbidtt " \
                 "WHERE t.best_file = 1 " \
                 "GROUP BY r.userId HAVING COUNT(r.movielensId) > 200 "

    c = conn.cursor()
    c.execute(queryUsers)
    all_users = c.fetchall()
    Users = random.sample(all_users, int(len(all_users)*0.1)) #Users for this iteration
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
          "WHERE userid = ?" \
          "AND EXISTS (SELECT movielensid FROM movielens_rating r WHERE r.movielensid = mm.movielensid) "

    c = conn.cursor()
    c.execute(sql, (user,))
    return c.fetchall()

# Randomly select items unrated by the user
def getRandomMovieSet(conn, user):
    sql = "SELECT 1, mm.movielensId, m.title, t.id " \
          "FROM movies m " \
          "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
          "JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 " \
          "WHERE EXISTS (SELECT movielensid FROM movielens_rating r WHERE r.movielensid = mm.movielensid) " \
          "AND CAST(imdbvotes AS NUMERIC) > 200 " \
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


def getMovieRatings1(conn, movie1, movie2):

    sqlI = "SELECT r1.rating FROM movielens_rating r1, movielens_rating r2 WHERE r1.userid = r2.userid " \
           "AND r1.movielensid = ? AND r2.movielensid = ? ORDER BY r1.userId"
    c = conn.cursor()
    c.execute(sqlI, (movie1, movie2,))
    ratings = c.fetchall()
    return ratings


def getMovieRatings2(conn, movie1, movie2):

    sqlI = "SELECT r2.rating FROM movielens_rating r1, movielens_rating r2 WHERE r1.userid = r2.userid " \
           "AND r1.movielensid = ? AND r2.movielensid = ? ORDER BY r1.userId"
    c = conn.cursor()
    c.execute(sqlI, (movie1, movie2,))
    ratings = c.fetchall()
    return ratings


def getUserInstances(userMovies, featureVector):

    all_features = []
    all_values = []

    for movie in userMovies:
        try:
            features = featureVector[movie[0]]
            all_features.append(features)
            all_values.append(movie[1])
        except KeyError:
            continue

    return all_features, all_values


# Return 70% of the user's rated movies
def getUserTrainingTestMovies(conn, user):
    sql = "SELECT t.id, r.rating, m.movielensid, m.title " \
          "FROM trailers t " \
          "JOIN movielens_movie m ON m.imdbidtt = t.imdbid " \
          "JOIN movielens_rating r ON r.movielensid = m.movielensid " \
          "JOIN movies ms ON ms.imdbid = t.imdbid " \
          "WHERE t.best_file = 1 " \
          "AND r.userid = ? " \
          "AND CAST(ms.imdbvotes AS NUMERIC) > 200 "
    c = conn.cursor()
    c.execute(sql, (user,))

    all_movies = c.fetchall()

    training_set = random.sample(all_movies, int(len(all_movies)*0.7))
    test_set = [x for x in all_movies if x not in training_set and x[1] > 4]

    return training_set, test_set


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
