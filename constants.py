import sqlite3
from utils import appendColumns

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

def appendQueryAllMovies():
    QUERY_ALL_MOVIES = ", mm.movielensId, m.title FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid LIMIT ?"
    return QUERY_ALL_MOVIES

def appendQueryMovie():
    QUERY_MOVIE = ", r.rating, mm.movielensId, m.title FROM movies m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid JOIN movielens_rating r ON r.movielensid = mm.movielensid WHERE r.userid = ? AND r.movielensId != ? LIMIT ?"
    return QUERY_MOVIE

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

def setQueries(RECOMMENDATION_STRATEGY):
    if (RECOMMENDATION_STRATEGY == "quanti"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendQuantitative()
    elif (RECOMMENDATION_STRATEGY == "quali"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendQualitative()
    elif (RECOMMENDATION_STRATEGY == "both"):
        QUERY_ALL_MOVIES, QUERY_MOVIE = recommendBothStrategies()

    return QUERY_ALL_MOVIES, QUERY_MOVIE
