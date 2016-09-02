import constants
from utils import isValid
import scipy
from scipy.spatial.distance import cosine

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

    return computeCosine(vI, vJ)

def computeGowerQualitative(i, j, RECOMMENDATION_STRATEGY):

    SumSijk, SumDeltaijk, bothFactor = 0, 0, 0

    if (RECOMMENDATION_STRATEGY == 'both'):
        bothFactor = len(constants.COLUMNS)

    for c in constants.COLUMNS_NOMINAL:
        iValue = i[constants.COLUMNS_NOMINAL.index(c)+bothFactor]
        jValue = j[constants.COLUMNS_NOMINAL.index(c)+bothFactor]
        #print iValue, jValue
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

#TODO apply weights
# i and j are items (movies)
def computeGowerSimilarity(i, j, RECOMMENDATION_STRATEGY, MIN, MAX):

    if (RECOMMENDATION_STRATEGY == 'quanti'):
        SumSijk, SumDeltaijk = computeGowerQuantitative(i, j, MIN, MAX)
    elif (RECOMMENDATION_STRATEGY == 'quali'):
        SumSijk, SumDeltaijk = computeGowerQualitative(i, j, RECOMMENDATION_STRATEGY)
    else: #both
        a1,b1 = computeGowerQuantitative(i, j, MIN, MAX)
        a2,b2 = computeGowerQualitative(i, j, RECOMMENDATION_STRATEGY)
        SumSijk, SumDeltaijk = (a1+a2), (b1+b2)

    if (SumDeltaijk == 0):
        return 0

    return (SumSijk / SumDeltaijk)

def computeAdjustedCosine(i, j, UserAverageRating):

    query = "SELECT "

    return

def computeSimilarity(SIMILARITY_MEASURE, movieI, movieJ, RECOMMENDATION_STRATEGY, MIN, MAX, UserAverageRating):
    if (SIMILARITY_MEASURE == 'gower'):
        sim = computeGowerSimilarity(movieI, movieJ, RECOMMENDATION_STRATEGY, MIN, MAX)
    elif (SIMILARITY_MEASURE == 'cos-content'):
        sim = computeCosineSimilarityContent(movieI, movieJ, RECOMMENDATION_STRATEGY)
    elif (SIMILARITY_MEASURE == 'cos-collaborative'):
        sim = computeCosineSimilarityCollaborative(movieI, movieJ)
    elif (SIMILARITY_MEASURE == 'adjusted-cosine'):
        sim = computeAdjustedCosine(movieI, movieJ, UserAverageRating)

    return sim
