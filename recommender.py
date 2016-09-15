import constants
from evaluation import evaluateMAE, evaluateUserPrecisionRecall
from similarity import computeFeaturesSimilarity


# for every item to predict, determine the class based on the proximity of k items that the user rated
def contentBasedKnn(Users, SelectedMovies, k=1):
    for user in Users:
        print "Computing for User ", user[0], "..."
        for movieI in SelectedMovies:
            AllSimilarities = []
            c = constants.conn.cursor()
            c.execute(constants.getQueryUserMovies(), (user[0], movieI[constants.INDEX_COLUMN_ID],))
            for userMovie in c.fetchall():
                sim = computeFeaturesSimilarity(movieI, userMovie)
                AllSimilarities.append((userMovie[constants.INDEX_COLUMN_TITLE+1], sim))
            print movieI[constants.INDEX_COLUMN_TITLE]
            print AllSimilarities
            return


def main(Users, SelectedMovies, simFunction):

    SumMAE, SumRecall, SumPrecision = 0, 0, 0

    for user in Users:
        print "Computing for User ", user[0], "..."
        predictions = []
        #Predict rating for each movie
        for movieI in SelectedMovies:
            prediction = predictUserRating(user, movieI, simFunction)
            predictions.append((movieI[constants.INDEX_COLUMN_ID], movieI[constants.INDEX_COLUMN_TITLE], prediction))

        topPredictions = sorted(predictions, key=lambda tup: tup[2], reverse=True)[:constants.PREDICTION_LIST_SIZE] # 2 is the index of the rating
        # print "Top Predictions ", topPredictions
        SumMAE += evaluateMAE(user[0], predictions) #predicted ratings for the same movies that the user rated
        predictionsIds = [int(x[0]) for x in topPredictions]
        recall, precision = evaluateUserPrecisionRecall(user[0], predictionsIds)
        SumRecall += recall
        SumPrecision += precision

    return SumMAE, SumRecall, SumPrecision

def predictUserRating(user, movieI, simFunction=computeFeaturesSimilarity):

    global SIMILARITY_MEASURE, RECOMMENDATION_STRATEGY, MIN, MAX

    SumSimilarityTimesRating, SumSimilarity = float(0), float(0)
    prediction = 0
    AllSimilarities = []
    # print "User ", user[0], " Movie ", movieI, " Value ", movieI[constants.INDEX_COLUMN_ID]
    c = constants.conn.cursor()
    c.execute(constants.getQueryUserMovies(), (user[0], movieI[constants.INDEX_COLUMN_ID],))

    #Find the k most similar items to I that the user also rated
    for movieJ in c.fetchall():
        # sim = computeSimilarity(movieI, movieJ)
        sim = simFunction(movieI, movieJ)
        AllSimilarities.append((movieJ, sim))

    #TODO Change this value
    kMostSimilar = sorted(AllSimilarities, key=lambda tup: tup[1], reverse=True)[:30] #index 1 is the similarity

    # print "Movie "
    # print movieI[constants.INDEX_COLUMN_TITLE], movieI[len(constants.COLUMNS)]
    # for k in kMostSimilar:
    #     print k[0][constants.INDEX_COLUMN_TITLE+1], k[0][len(constants.COLUMNS)], k[1]
    # exit()

    for k in kMostSimilar:
        movieJ = k[0]
        sim = k[1]
        SumSimilarityTimesRating += (sim * float(movieJ[constants.INDEX_COLUMN_RATING]))
        SumSimilarity += abs(sim)

    if (SumSimilarityTimesRating > 0 and SumSimilarity > 0):
        prediction = SumSimilarityTimesRating / SumSimilarity

    return prediction

if __name__ == '__main__':
    main()
