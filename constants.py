import sqlite3
from utils import appendColumns
from opening_feat import load_features

conn = sqlite3.connect('database.db')

CURSOR_USERS = conn.cursor()
CURSOR_MOVIES = conn.cursor()
CURSOR_USERMOVIES = conn.cursor()
CURSOR_MOVIEI = conn.cursor()
CURSOR_MOVIEJ = conn.cursor()

SEPARATOR = ","

PREDICTION_LIST_SIZE = 20
LIMIT_ITEMS_TO_PREDICT = 4000
LIMIT_ITEMS_TO_COMPARE = 25
NUM_USERS = 1

MAX_NUM_USERS = 19042
MAX_ITEMS_TO_PREDICT = 3248
MAX_ITEMS_TO_COMPARE = 1671

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

# For Quantitative Columns Only
INDEX_COLUMN_ID = len(COLUMNS)
INDEX_COLUMN_TITLE = len(COLUMNS)+1
INDEX_COLUMN_RATING = len(COLUMNS)
INDEX_COLUMN_TRAILER_ID_ALL_MOVIES = len(COLUMNS)+2
INDEX_COLUMN_TRAILER_ID_USER_MOVIE = len(COLUMNS)+3

def appendQueryAllMovies():
    QUERY_ALL_MOVIES = ", mm.movielensId, m.title, t.id FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 LIMIT ?"
    return QUERY_ALL_MOVIES

def appendQueryMovie():
    QUERY_MOVIE = ", r.rating, mm.movielensId, m.title, t.id FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid JOIN movielens_rating r ON r.movielensid = mm.movielensid JOIN trailers t ON t.imdbID = m.imdbID AND t.best_file = 1 WHERE r.userid = ? AND r.movielensId != ? LIMIT ?"
    return QUERY_MOVIE

def recommendQuantitative():
    QUERY_ALL_MOVIES = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+appendQueryAllMovies()
    QUERY_MOVIE = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+appendQueryMovie()

    return QUERY_ALL_MOVIES, QUERY_MOVIE

def recommendQualitative():
    global INDEX_COLUMN_ID, INDEX_COLUMN_TITLE, INDEX_COLUMN_RATING, INDEX_COLUMN_TRAILER_ID_ALL_MOVIES, INDEX_COLUMN_TRAILER_ID_USER_MOVIE

    QUERY_ALL_MOVIES = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryAllMovies()
    QUERY_MOVIE = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryMovie()

    INDEX_COLUMN_ID = len(COLUMNS_NOMINAL)
    INDEX_COLUMN_TITLE = len(COLUMNS_NOMINAL)+1
    INDEX_COLUMN_RATING = len(COLUMNS_NOMINAL)
    INDEX_COLUMN_TRAILER_ID_ALL_MOVIES = len(COLUMNS_NOMINAL)+2
    INDEX_COLUMN_TRAILER_ID_USER_MOVIE = len(COLUMNS_NOMINAL)+3

    return QUERY_ALL_MOVIES, QUERY_MOVIE

def recommendBothStrategies():
    global INDEX_COLUMN_ID, INDEX_COLUMN_TITLE, INDEX_COLUMN_RATING, INDEX_COLUMN_TRAILER_ID_ALL_MOVIES, INDEX_COLUMN_TRAILER_ID_USER_MOVIE

    QUERY_ALL_MOVIES = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+","+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryAllMovies()
    QUERY_MOVIE = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+","+SEPARATOR.join(appendColumns(COLUMNS_NOMINAL))+appendQueryMovie()

    INDEX_COLUMN_ID = len(COLUMNS)+len(COLUMNS_NOMINAL)
    INDEX_COLUMN_TITLE = len(COLUMNS)+len(COLUMNS_NOMINAL)+1
    INDEX_COLUMN_RATING = len(COLUMNS)+len(COLUMNS_NOMINAL)
    INDEX_COLUMN_TRAILER_ID_ALL_MOVIES = len(COLUMNS)+len(COLUMNS_NOMINAL)+2
    INDEX_COLUMN_TRAILER_ID_USER_MOVIE = len(COLUMNS)+len(COLUMNS_NOMINAL)+3

    return QUERY_ALL_MOVIES, QUERY_MOVIE

def setQueries(RECOMMENDATION_STRATEGY):
    if (RECOMMENDATION_STRATEGY == "quanti"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendQuantitative()
    elif (RECOMMENDATION_STRATEGY == "quali"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendQualitative()
    elif (RECOMMENDATION_STRATEGY == "both" or RECOMMENDATION_STRATEGY == "triple"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendBothStrategies()

    return QUERY_ALL_MOVIES, QUERY_MOVIE
