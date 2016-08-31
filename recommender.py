import sqlite3
import scipy
import numpy.linalg as LA
import numpy as np
from scipy.spatial.distance import cosine

conn = sqlite3.connect('database.db')
CURSOR_USERS = conn.cursor()
CURSOR_MOVIES = conn.cursor()
CURSOR_USERMOVIES = conn.cursor()
CURSOR_VALUE = conn.cursor()
CURSOR_MOVIEI = conn.cursor()
CURSOR_MOVIEJ = conn.cursor()

MOVIE_TABLE_NAME = "movies"
INVALID = 'N/A'
SEPARATOR = ","
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
MIN = []
MAX = []

def loadMinMaxValues():
    for c in COLUMNS:
        MIN.append(float(getValue('MIN', c)))
        MAX.append(float(getValue('MAX', c)))

def main():

    loadMinMaxValues()
    #print "MIN", MIN, "MAX", MAX
    predictions = []

    query_all_movies = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+", mm.movielensId, m.title FROM "+MOVIE_TABLE_NAME+" m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid LIMIT 20"
    query = "SELECT userid FROM movielens_user LIMIT 1"

    for user in CURSOR_USERS.execute(query):
        print "Computing for User ", user[0], "..."
        query_movie = "SELECT "+SEPARATOR.join(appendColumns(COLUMNS))+", r.rating, mm.movielensId, m.title FROM "+MOVIE_TABLE_NAME+" m JOIN movielens_movie mm ON mm.imdbidtt = m.imdbid JOIN movielens_rating r ON r.movielensid = mm.movielensid WHERE r.userid = ? AND r.movielensId != ? LIMIT 20"
        #print query_all_movies, query_movie
        for movieI in CURSOR_MOVIES.execute(query_all_movies): #will predict rating to all movies

            prediction = predictUserRating(query_movie, user, movieI)
            predictions.append((movieI[len(COLUMNS)+1], movieI[len(COLUMNS)], prediction))

    print sorted(predictions, key=lambda tup: tup[2], reverse=True)[:20]
    conn.close()

def predictUserRating(query_movie, user, movieI):

    SumSimilarityTimesRating = float(0)
    SumSimilarity = float(0)
    prediction = 0 #TODO replace with baseline prediction

    #get all rated movies by current user (except the current movieI)
    for movieJ in CURSOR_USERMOVIES.execute(query_movie, (user[0], movieI[len(COLUMNS)])):
        #sim = computeGowerSimilarity(movieI, movieJ)
        sim = computeCosineSimilarity(movieI, movieJ)
        #print movieJ[len(COLUMNS)+2], sim, movieJ[len(COLUMNS)]

        SumSimilarityTimesRating += (sim * movieJ[len(COLUMNS)])
        SumSimilarity += abs(sim)

    if (SumSimilarityTimesRating > 0 and SumSimilarity > 0):
        prediction = SumSimilarityTimesRating / SumSimilarity

    return prediction

def computeCosineSimilarity(i, j):
    movieIid = i[len(COLUMNS)]
    movieJid = j[len(COLUMNS)+1]

    CURSOR_MOVIEI.execute("SELECT rating FROM movielens_rating r WHERE r.movielensID = ? AND EXISTS (SELECT * FROM movielens_rating r2 WHERE r2.movielensID = ? AND r2.userId = r.userId)", (movieIid,movieJid,))
    CURSOR_MOVIEJ.execute("SELECT rating FROM movielens_rating r WHERE r.movielensID = ? AND EXISTS (SELECT * FROM movielens_rating r2 WHERE r2.movielensID = ? AND r2.userId = r.userId)", (movieJid,movieIid,))
    a = scipy.array(CURSOR_MOVIEI.fetchall())
    b = scipy.array(CURSOR_MOVIEJ.fetchall())

    return cosine(a, b)

    #return 0
    #return cosine_similarity(ratingsI, ratingsJ)
    #return cosine(ratingsI, ratingsJ)

#TODO categorical / nominal attributes
#TODO apply weights
#i and j are items (movies)
def computeGowerSimilarity(i, j):

    SumSijk = float(0)
    SumDeltaijk = float(0)

    for c in COLUMNS:

        iValue = float(i[COLUMNS.index(c)])
        jValue = float(j[COLUMNS.index(c)])
        #print iValue, jValue

        if (isValid(iValue) and isValid(jValue)):
            Deltaijk = 1
            diff = abs(iValue - jValue)
            #Sijk = 1 - (diff / (getValue('MAX', c) - getValue('MIN', c)) )
            Sijk = 1 - (diff / (MAX[COLUMNS.index(c)] - MIN[COLUMNS.index(c)]) )
        else:
            Sijk = 0
            Deltaijk = 0

        SumDeltaijk += Deltaijk
        SumSijk += Sijk

    if (SumDeltaijk == 0):
        return 0

    #print SumSijk, SumDeltaijk, (SumSijk / SumDeltaijk)

    return (SumSijk / SumDeltaijk)

def getValue(function, attribute):
    if (function == 'MIN'):
        function = "MAX(MIN("+attribute+"), 0)"
    else:
        function = "MAX("+attribute+")"
    #query = "SELECT "+function+"("+attribute+") FROM "+MOVIE_TABLE_NAME+" WHERE "+attribute+" != '"+INVALID+"'"
    query = "SELECT "+function+" FROM "+MOVIE_TABLE_NAME+" WHERE "+attribute+" != '"+INVALID+"'"
    #print query
    CURSOR_VALUE.execute(query)
    return CURSOR_VALUE.fetchone()[0]

def isValid(item):
    return item != INVALID

def appendColumns(columns):
    columnList = []
    for c in columns:
        columnList.append(c)
    return columnList

if __name__ == '__main__':
    main()
