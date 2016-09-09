import sqlite3
from utils import appendColumns
from opening_feat import load_features

conn = sqlite3.connect('database.db')

SEPARATOR = ","

PREDICTION_LIST_SIZE = 20
LIMIT_ITEMS_TO_PREDICT = 10
NUM_USERS = 1

MIN_FEATURE_VALUE = -1
MAX_FEATURE_VALUE = 1

FEATURES = load_features('res_neurons_128_feat_1024_scenes_350.bin') #dictionary

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

INDEX_COLUMN_ID = len(COLUMNS)+len(COLUMNS_NOMINAL)
INDEX_COLUMN_TITLE = len(COLUMNS)+len(COLUMNS_NOMINAL)+1
INDEX_COLUMN_RATING = len(COLUMNS)+len(COLUMNS_NOMINAL)
INDEX_COLUMN_TRAILER_ID_ALL_MOVIES = len(COLUMNS)+len(COLUMNS_NOMINAL)+2
INDEX_COLUMN_TRAILER_ID_USER_MOVIE = len(COLUMNS)+len(COLUMNS_NOMINAL)+3

def appendQueryAllMovies():
    QUERY_ALL_MOVIES = ", mm.movielensId, m.title, t.id FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1"
    return QUERY_ALL_MOVIES

def appendQueryMovie():
    QUERY_MOVIE = ", r.rating, mm.movielensId, m.title, t.id FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid JOIN movielens_rating r ON r.movielensid = mm.movielensid JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 WHERE r.userid = ? AND r.movielensId != ?"
    return QUERY_MOVIE

def getQueryAllMovies():
    global COLUMNS, COLUMNS_NOMINAL, SEPARATOR

    QUERY_ALL_MOVIES = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+","+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryAllMovies()

    return QUERY_ALL_MOVIES

def getQueryUserMovies():
    global COLUMNS, COLUMNS_NOMINAL, SEPARATOR

    QUERY_MOVIE = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+","+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryMovie()

    return QUERY_MOVIE
