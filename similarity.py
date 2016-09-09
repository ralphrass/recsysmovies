import constants
from utils import isValid
import scipy
from scipy.spatial.distance import cosine
from math import sqrt

def computeCosine(i, j):
    a = scipy.array(i)
    b = scipy.array(j)
    if (a.size == 0 and b.size == 0):
        return 0
    else:
        return cosine(a, b)

def computeCosineSimilarityCollaborative(i, j):
    movieIid = i[constants.INDEX_COLUMN_ID]
    movieJid = j[constants.INDEX_COLUMN_ID]

    constants.CURSOR_MOVIEI.execute("SELECT rating FROM movielens_rating r WHERE r.movielensID = ? AND EXISTS (SELECT * FROM movielens_rating r2 WHERE r2.movielensID = ? AND r2.userId = r.userId)", (movieIid,movieJid,))
    constants.CURSOR_MOVIEJ.execute("SELECT rating FROM movielens_rating r WHERE r.movielensID = ? AND EXISTS (SELECT * FROM movielens_rating r2 WHERE r2.movielensID = ? AND r2.userId = r.userId)", (movieJid,movieIid,))
    return computeCosine(CURSOR_MOVIEI.fetchall(), CURSOR_MOVIEJ.fetchall())

##TODO cosine qualitative
def computeCosineSimilarityContent(i, j, RECOMMENDATION_STRATEGY):
    vI, vJ = [], []

    if (RECOMMENDATION_STRATEGY == 'quanti'):
        for c in constants.COLUMNS:
            iValue = float(i[constants.COLUMNS.index(c)])
            jValue = float(j[constants.COLUMNS.index(c)])
            if (isValid(iValue) and isValid(jValue)):
                vI.append(iValue)
                vJ.append(jValue)

    if (RECOMMENDATION_STRATEGY == 'triple'): #include features
        featuresI = constants.FEATURES[i[constants.INDEX_COLUMN_TRAILER_ID_ALL_MOVIES]]
        featuresJ = constants.FEATURES[j[constants.INDEX_COLUMN_TRAILER_ID_USER_MOVIE]]
        vI.extend(featuresI)
        vJ.extend(featuresJ)

    if (not vI) and (not vJ):
        return 0
    else:
        return computeCosine(vI, vJ)

def computeCosineSimilarityFeatures(i, j):
    featuresI = constants.FEATURES[i[constants.INDEX_COLUMN_TRAILER_ID_ALL_MOVIES]]
    featuresJ = constants.FEATURES[j[constants.INDEX_COLUMN_TRAILER_ID_USER_MOVIE]]

    return computeCosine(featuresI, featuresJ)

def computeGowerQualitative(i, j, RECOMMENDATION_STRATEGY):

    SumSijk, SumDeltaijk = 0, 0

    for c in constants.COLUMNS_NOMINAL:
        iValue = i[constants.COLUMNS_NOMINAL.index(c)+len(constants.COLUMNS)]
        jValue = j[constants.COLUMNS_NOMINAL.index(c)+len(constants.COLUMNS)]
        # print iValue, jValue
        if (isValid(iValue) and isValid(jValue)):
            if (c == "genre" or c == "actors"):
                values = iValue.split(constants.NOMINAL_SPLIT[constants.COLUMNS_NOMINAL.index(c)])
                for val in values:
                    if val in jValue:
                        SumSijk += 1
                        SumDeltaijk += 1
            else:
                if (iValue == jValue):
                    SumSijk += 1
                    SumDeltaijk += 1

    return SumSijk, SumDeltaijk

def computeGowerQuantitative(i, j, MIN, MAX):

    SumSijk, SumDeltaijk = float(0), float(0)

    for c in constants.COLUMNS:
        iValue = float(i[constants.COLUMNS.index(c)])
        jValue = float(j[constants.COLUMNS.index(c)])

        if (isValid(iValue) and isValid(jValue)):
            Deltaijk = 1
            diff = abs(iValue - jValue)
            Sijk = 1 - (diff / (MAX[constants.COLUMNS.index(c)] - MIN[constants.COLUMNS.index(c)]) )
        else:
            Sijk, Deltaijk = 0, 0

        SumDeltaijk += Deltaijk
        SumSijk += Sijk

    return SumSijk, SumDeltaijk

def computeGowerFeatures(i, j):
    SumSijk, SumDeltaijk = float(0), float(0)

    featuresI = constants.FEATURES[i[constants.INDEX_COLUMN_TRAILER_ID_ALL_MOVIES]]
    featuresJ = constants.FEATURES[j[constants.INDEX_COLUMN_TRAILER_ID_USER_MOVIE]]

    for i in range(len(featuresI)):

        iValue = float(featuresI[i])
        jValue = float(featuresJ[i])

        Deltaijk = 1
        diff = float(abs(iValue - jValue))
        Sijk = 1 - (diff / (constants.MAX_FEATURE_VALUE - constants.MIN_FEATURE_VALUE) )

        SumDeltaijk += Deltaijk
        SumSijk += Sijk

    return SumSijk, SumDeltaijk

#TODO apply weights
# i and j are items (movies)
def computeGowerSimilarity(i, j, RECOMMENDATION_STRATEGY, MIN, MAX):

    if (RECOMMENDATION_STRATEGY == 'quanti'):
        SumSijk, SumDeltaijk = computeGowerQuantitative(i, j, MIN, MAX)
    elif (RECOMMENDATION_STRATEGY == 'quali'):
        SumSijk, SumDeltaijk = computeGowerQualitative(i, j, RECOMMENDATION_STRATEGY)
    elif (RECOMMENDATION_STRATEGY == 'triple'):
        a1,b1 = computeGowerQuantitative(i, j, MIN, MAX)
        a2,b2 = computeGowerFeatures(i, j)
        SumSijk, SumDeltaijk = (a1+a2), (b1+b2)
    # elif (RECOMMENDATION_STRATEGY == 'triple'):
    #     a1,b1 = computeGowerQuantitative(i, j, MIN, MAX)
    #     a2,b2 = computeGowerQualitative(i, j, RECOMMENDATION_STRATEGY)
    #     a3,b3 = computeGowerFeatures(i, j)
    #     SumSijk, SumDeltaijk = (a1+a2+a3), (b1+b2+b3)
    else: #both
        a1,b1 = computeGowerQuantitative(i, j, MIN, MAX)
        a2,b2 = computeGowerQualitative(i, j, RECOMMENDATION_STRATEGY)
        SumSijk, SumDeltaijk = (a1+a2), (b1+b2)

    if (SumDeltaijk == 0):
        return 0

    return (SumSijk / SumDeltaijk)

def computeAdjustedCosine(i, j):

    SumNumerator, SumDenominator1, SumDenominator2 = 0, 0, 0

    # Select users that rated both movies
    query = "SELECT r.userId FROM movielens_rating r WHERE r.movielensId = ? INTERSECT SELECT r.userId FROM movielens_rating r WHERE r.movielensId = ?"
    constants.CURSOR_MOVIEI.execute(query, (i[constants.INDEX_COLUMN_ID],j[constants.INDEX_COLUMN_ID]))
    users = constants.CURSOR_MOVIEI.fetchall()

    if not users:
        return 0
    else:
        for user in users:

            query = "SELECT SUM(r.rating)/COUNT(*) FROM movielens_rating r WHERE r.userId = ?"
            constants.CURSOR_MOVIEI.execute(query, (user[0]))
            userAverage = constants.CURSOR_MOVIEI.fetchone()

            query = "SELECT r.rating FROM movielens_rating r WHERE r.userId = ? AND r.movielensId = ?"

            constants.CURSOR_MOVIEJ.execute(query, (user[0], i[constants.INDEX_COLUMN_ID]))
            ratingMovieI = constants.CURSOR_MOVIEJ.fetchone()

            constants.CURSOR_MOVIEJ.execute(query, (user[0], j[constants.INDEX_COLUMN_ID]))
            ratingMovieJ = constants.CURSOR_MOVIEJ.fetchone()

            print "User ", user[0], " average ", userAverage, " Rating ", ratingMovieI, " Rating 2 ", ratingMovieJ

            SumNumerator += ( (ratingMovieI - userAverage) * (ratingMovieJ - userAverage) )
            SumDenominator1 += (ratingMovieI - userAverage)**2
            SumDenominator2 += (ratingMovieJ - userAverage)**2

        return SumNumerator / (sqrt(SumDenominator1) * sqrt(SumDenominator2))

def computeSimilarity(SIMILARITY_MEASURE, movieI, movieJ, RECOMMENDATION_STRATEGY, MIN, MAX):
    if (SIMILARITY_MEASURE == 'gower'):
        sim = computeGowerSimilarity(movieI, movieJ, RECOMMENDATION_STRATEGY, MIN, MAX)
    elif (SIMILARITY_MEASURE == 'cos-content' and (RECOMMENDATION_STRATEGY == 'quanti' or RECOMMENDATION_STRATEGY == 'triple')):
        sim = computeCosineSimilarityContent(movieI, movieJ, RECOMMENDATION_STRATEGY)
    elif (SIMILARITY_MEASURE == 'cos-collaborative'):
        sim = computeCosineSimilarityCollaborative(movieI, movieJ)
    elif (SIMILARITY_MEASURE == 'adjusted-cosine'):
        sim = computeAdjustedCosine(movieI, movieJ)
    elif (SIMILARITY_MEASURE == 'gower-features' and (RECOMMENDATION_STRATEGY == 'quanti')):
        SumSijk, SumDeltaijk = computeGowerFeatures(movieI, movieJ)
        sim = SumSijk / SumDeltaijk
    elif (SIMILARITY_MEASURE == 'cos-features' and (RECOMMENDATION_STRATEGY == 'quanti')):
        sim = computeCosineSimilarityFeatures(movieI, movieJ)
    else:
        sim = 0

    return sim
