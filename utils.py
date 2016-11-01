import io
import numpy as np
import random
import sqlite3
from opening_feat import load_features
import itertools as it
import pandas as pd
from sklearn import preprocessing


# conn = sqlite3.connect('database.db')

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


def selectRandomUsers(conn, limit1, limit2):

    # queryUsers = "SELECT u.userid, u.avgrating " \
    # queryUsers = "SELECT DISTINCT u.userid, u.avgrating " \
    #              "FROM movielens_user u " \
    #              "JOIN movielens_rating r ON r.userId = u.userId " \
    #              "JOIN movielens_movie m ON m.movielensid = r.movielensid " \
    #              "JOIN trailers t ON t.imdbid = m.imdbidtt " \
    #              "WHERE t.best_file = 1 "
                 # "GROUP BY r.userId HAVING COUNT(r.movielensId) > 200 " \
                 # "LIMIT 1 "
    queryUsers = "SELECT u.userid, u.avgrating " \
                 "FROM movielens_user_trailer u "\
                 "LIMIT ?, ?"

    c = conn.cursor()
    c.execute(queryUsers, (limit1, limit2,))
    # c.execute(queryUsers)
    all_users = c.fetchall()
    return all_users


    # if n is None:
    #     return all_users
    #
    # limit = int(len(all_users)*n)
    # Users = random.sample(all_users, limit)
    #
    # return Users


# def selectTrainingMovies(conn):
#
#     query = "SELECT 1, mm.movielensId, m.title, t.id " \
#             "FROM movies m " \
#             "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
#             "JOIN trailers t ON t.imdbID = m.imdbID " \
#             "AND t.best_file = 1 " \
#             # "AND CAST(imdbvotes AS NUMERIC) > 5"
#
#     c = conn.cursor()
#     c.execute(query)
#     # SelectedMovies = random.sample(c.fetchall(), limit)
#     SelectedMovies = c.fetchall()
#
#     return SelectedMovies

# def getUserMovies(conn, user):
#     sql = "SELECT r.rating, mm.movielensId, m.title, t.id " \
#           "FROM movies m " \
#           "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
#           "JOIN movielens_rating r ON r.movielensid = mm.movielensid " \
#           "JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 " \
#           "WHERE r.userid = ? "
#     # print sql, user
#     c = conn.cursor()
#     c.execute(sql, (user,))
#     return c.fetchall()

# Equal to 5 stars ==> [Greater than 4 stars]
# def getEliteTestRatingSet(conn, user):
#     sql = "SELECT m.rating , m.movielensid, mm.title, t.id " \
#           "FROM movielens_rating_elite m " \
#           "JOIN movielens_movie mm ON mm.movielensid = m.movielensid " \
#           "JOIN trailers t ON t.imdbID = mm.imdbIDtt " \
#           "AND t.best_file = 1 " \
#           "WHERE userid = ?" \
#           "AND EXISTS (SELECT movielensid FROM movielens_rating r WHERE r.movielensid = mm.movielensid) "
#
#     c = conn.cursor()
#     c.execute(sql, (user,))
#     return c.fetchall()

# Randomly select items unrated by the user
def getRandomMovieSet(user):
    # sql = "SELECT 1, mm.movielensId, m.title, t.id " \
    # sql = "SELECT t.id, 1, mm.movielensId, m.title " \

    conn = sqlite3.connect('database.db')

    sql = "SELECT t.id, 1, mm.movielensId " \
          "FROM movies m " \
          "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
          "JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 " \
          "WHERE EXISTS (SELECT movielensid FROM movielens_rating r WHERE r.movielensid = mm.movielensid) " \
          "EXCEPT " \
          "SELECT t.id, 1, mm.movielensId " \
          "FROM movies m " \
          "JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid " \
          "JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 " \
          "JOIN movielens_rating r ON r.movielensid = mm.movielensid " \
          "WHERE r.userid = ? "

    # "AND CAST(imdbvotes AS NUMERIC) > 200 " \
    # print sql, user
    limit = 100
    c = conn.cursor()
    c.execute(sql, (user,))
    all_movies = c.fetchall()
    if len(all_movies) == 0:
        return 0

    Movies = random.sample(all_movies, limit)
    # print Movies

    # conn.close()

    return Movies

def get_user_baseline(userid, _ratings, _global_average):

    return _ratings.loc[userid]['average'] - _global_average

    # user_ratings = _ratings.loc[userid]

    # return user_ratings['rating'].mean() - _global_average

    # return user_ratings['rating'].sum() / len(user_ratings) - _global_average


# def getUserBaseline(user):
#
#     global _global_average
#
#     conn = sqlite3.connect('database.db')
#
#     sql = "SELECT SUM(rating)/COUNT(rating) " \
#           "FROM movielens_rating " \
#           "WHERE userid = ?"
#     # print sql, user
#     c = conn.cursor()
#     c.execute(sql, (user,))
#
#     # conn.close()
#
#     return c.fetchone()[0] - _global_average


def get_item_baseline(user_baseline, movieid, _ratings_by_movie, _global_average):

    return _ratings_by_movie.loc[movieid]['average'] - user_baseline - _global_average

    # movie_ratings = _ratings_by_movie[_ratings_by_movie.movielensID == movieid]

    # return movie_ratings['rating'].mean() - user_baseline - _global_average



# def getItemBaseline(userbaseline, movie):
#
#     global _global_average
#
#     conn = sqlite3.connect('database.db')
#
#     sql = "SELECT SUM(rating)/COUNT(rating) " \
#           "FROM movielens_rating " \
#           "WHERE movielensid = ?"
#     # print sql, userbaseline, movie
#     c = conn.cursor()
#     c.execute(sql, (movie,))
#
#     # conn.close()
#
#     return c.fetchone()[0] - userbaseline - _global_average


# def getUserAverageRating(conn, user):
#
#     # queryUserAverage = "SELECT SUM(rating)/COUNT(*) FROM movielens_rating WHERE userId = ?"
#     queryUserAverage = "SELECT avgrating FROM movielens_user WHERE userId = ?"
#
#     c = conn.cursor()
#     c.execute(queryUserAverage, (user,))
#     UserAverageRating = float(c.fetchone()[0])
#
#     return UserAverageRating


# def getMovieRatings1(conn, movie1, movie2):
#
#     sqlI = "SELECT r1.rating FROM movielens_rating r1, movielens_rating r2 WHERE r1.userid = r2.userid " \
#            "AND r1.movielensid = ? AND r2.movielensid = ? ORDER BY r1.userId"
#     c = conn.cursor()
#     c.execute(sqlI, (movie1, movie2,))
#     ratings = c.fetchall()
#     return ratings
#
#
# def getMovieRatings2(conn, movie1, movie2):
#
#     sqlI = "SELECT r2.rating FROM movielens_rating r1, movielens_rating r2 WHERE r1.userid = r2.userid " \
#            "AND r1.movielensid = ? AND r2.movielensid = ? ORDER BY r1.userId"
#     c = conn.cursor()
#     c.execute(sqlI, (movie1, movie2,))
#     ratings = c.fetchall()
#     return ratings


def getUserInstances(userMovies, featureVector):

    all_features = []
    all_values = []

    for movie in userMovies:
        try:
            features = featureVector[movie[0]]
            all_features.append(list(features))
            all_values.append(movie[1])
        except KeyError:
            continue

    return all_features, all_values


# Return a percentage of the user's rated movies
def getUserTrainingTestMovies(user):
    # sql = "SELECT t.id, r.rating, m.movielensid, m.title " \

    conn = sqlite3.connect('database.db')

    sql = "SELECT t.id, r.rating, m.movielensid " \
          "FROM trailers t " \
          "JOIN movielens_movie m ON m.imdbidtt = t.imdbid " \
          "JOIN movielens_rating r ON r.movielensid = m.movielensid " \
          "JOIN movies ms ON ms.imdbid = t.imdbid " \
          "WHERE t.best_file = 1 " \
          "AND r.userid = ? "
    c = conn.cursor()
    c.execute(sql, (user,))
    all_movies = c.fetchall()
    elite_test_set = filter((lambda x: x[1] > 4), all_movies)  # good movies for each user
    garbage_test_set = filter((lambda x: x[1] < 3), all_movies)  # bad movies for each user

    # conn.close()

    return elite_test_set, all_movies, garbage_test_set

    # sql = "SELECT t.id, r.rating, m.movielensid " \
    #       "FROM trailers t " \
    #       "JOIN movielens_movie m ON m.imdbidtt = t.imdbid " \
    #       "JOIN movielens_rating r ON r.movielensid = m.movielensid " \
    #       "JOIN movies ms ON ms.imdbid = t.imdbid " \
    #       "WHERE t.best_file = 1 " \
    #       "AND r.userid = ? " \
    #       # "AND CAST(ms.imdbvotes AS NUMERIC) > 100 "
    # c = conn.cursor()
    # c.execute(sql, (user,))
    #
    # all_movies = c.fetchall()
    #
    # try:
    #     training_set = random.sample(all_movies, int(len(all_movies)*0.8))
    #     full_test_set = [x for x in all_movies if x not in training_set]
    #     elite_test_set = []
    #     for item in full_test_set:
    #         if item[1] > 4:
    #             elite_test_set.append(item)
    # except:
    #     raise
    #
    # return training_set, elite_test_set, full_test_set, all_movies


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


def get_similarity_matrices():

    similarities_low_level = load_features('movie_cosine_similarities_low_level.bin')
    similarities_deep = load_features('movie_cosine_similarities_deep.bin')
    similarities_hybrid = load_features('movie_cosine_similarities_hybrid.bin')

    return [similarities_low_level, similarities_deep, similarities_hybrid]


def extract_features(deep_feautures='resnet_152_lstm_128.dct'):

    LOW_LEVEL_FEATURES = load_features('low_level_dict.bin')
    arr = np.array([x[1] for x in LOW_LEVEL_FEATURES.iteritems()])
    scaler = preprocessing.StandardScaler().fit(arr)
    std = scaler.transform(arr)
    LOW_LEVEL_FEATURES = {k: v for k, v in it.izip(LOW_LEVEL_FEATURES.keys(), std)}

    DEEP_FEATURES = load_features(deep_feautures)
    # DEEP_FEATURES = load_features('bof_128.bin')
    arr = np.array([x[1] for x in DEEP_FEATURES.iteritems()])
    scaler = preprocessing.StandardScaler().fit(arr)
    std = scaler.transform(arr)
    DEEP_FEATURES = {k: v for k, v in it.izip(DEEP_FEATURES.keys(), std)}

    HYBRID_FEATURES = {}

    for k in DEEP_FEATURES.iterkeys():
        try:
            HYBRID_FEATURES[k] = np.append(DEEP_FEATURES[k], LOW_LEVEL_FEATURES[k])
        except KeyError:
            continue

    # arr = np.array([x[1] for x in HYBRID_FEATURES.iteritems()])
    # scaler = preprocessing.StandardScaler().fit(arr)
    # std = scaler.transform(arr)
    # HYBRID_FEATURES = {k: v for k, v in it.izip(HYBRID_FEATURES.keys(), std)}

    return LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES


def extract_tfidf_features():
    user_features = load_features('users_tfidf_profile.bin')
    movie_features = load_features('movies_tfidf_profile.bin')

    return user_features, movie_features
