import constants
import recommender
import evaluation
import utils
import time
from similarity import computeAdjustedCosine, computeFeaturesSimilarity, computeFeaturesAndRatingsSimilarity

MEASURES = [
    # "gower",
    "cos-content",
    # "gower-features",
    "cos-features",
    # "cos-collaborative",
    # "adjusted-cosine"
]

STRATEGIES = [
    "quanti", #quantitative features (MovieLens Rating, IMDB Rating, Tomato Rating, Tomato User Rating, Metascore)
    # "quali", #Actors, Director, Writer
    # "both", #quanti + quali
    #"triple" #both + features from trailers
]

def main():

    constants.NUM_USERS = 1 # constants.MAX_NUM_USERS
    constants.PREDICTION_LIST_SIZE = 50 #increase at each iteration - important to measure Recall
    constants.LIMIT_ITEMS_TO_PREDICT = 100 #constants.MAX_ITEMS_TO_PREDICT #list of all movies
    iterations = 1
    LIST_INCREASE = 25

    print "Starting Experiment... ", iterations, "iterations.", constants.NUM_USERS, "users.", "recommender list size equal to", constants.PREDICTION_LIST_SIZE, "." , constants.LIMIT_ITEMS_TO_PREDICT, "items to predict for"

    for i in range(iterations):

        print i, "iteration."

        Users = utils.selectRandomUsers()
        MoviesToPredict = utils.selectRandomMovies()

        mae, recall, precision = recommender.main(Users, MoviesToPredict, computeFeaturesAndRatingsSimilarity)
        print "MAE ", mae, " Recall ", recall, "Precision ", precision
        # return

        recommender.contentBasedKnn(Users, MoviesToPredict, 1)

        SumMAECollaborative, SumRecallCollaborative, SumPrecisionCollaborative = recommender.main(Users, MoviesToPredict,
                                                                                   computeAdjustedCosine)

        AVG_MAE_Collaborative = utils.evaluateAverage(SumMAECollaborative, constants.NUM_USERS)
        AVG_RECALL_Collaborative = utils.evaluateAverage(SumRecallCollaborative, constants.NUM_USERS)
        AVG_PRECISION_Collaborative = utils.evaluateAverage(SumPrecisionCollaborative, constants.NUM_USERS)

        print "MAE Collaborative ", AVG_MAE_Collaborative, "Recall Collaborative ", AVG_RECALL_Collaborative, " Precision Collaborative ", \
            AVG_PRECISION_Collaborative

        SumMAE, SumRecall, SumPrecision = recommender.main(Users, MoviesToPredict, computeFeaturesSimilarity)

        AVG_MAE = utils.evaluateAverage(SumMAE, constants.NUM_USERS)
        AVG_RECALL = utils.evaluateAverage(SumRecall, constants.NUM_USERS)
        AVG_PRECISION = utils.evaluateAverage(SumPrecision, constants.NUM_USERS)



        constants.LIMIT_ITEMS_TO_PREDICT += LIST_INCREASE

        UserAverageMAE = evaluation.evaluateRandomMAE(Users, MoviesToPredict)
        RandomMAE = evaluation.evaluateRandomMAE(Users, MoviesToPredict, False)

        RandomRecall, RandomPrecision = evaluation.evaluateRandomPrecisionRecall(Users, MoviesToPredict)
        print "Random Precision", RandomPrecision, "Random Recall", RandomRecall

        writeResults(iterations, LIST_INCREASE, i, UserAverageMAE, RandomMAE, AVG_MAE, AVG_RECALL, AVG_PRECISION, RandomRecall, RandomPrecision)

        print "User Average MAE ", (UserAverageMAE)
        print "Random MAE ", (RandomMAE)

    constants.conn.close()

def writeResults(iterations, LIST_INCREASE, i, UserAverageMAE, RandomMAE, AVG_MAE, AVG_RECALL, AVG_PRECISION, RandomRecall, RandomPrecision):

    FILE_NAME = time.strftime('%d-%m-%Y')+'-imageNet-LSTM-128-'+str(constants.NUM_USERS)+'users-'+str(constants.LIMIT_ITEMS_TO_PREDICT)+'items-1iterations-'+str(iterations)+'Plus-List'+str(LIST_INCREASE)+'.txt'

    with open(FILE_NAME, 'a') as resfile:
        striteration = str(i)+" iteration\n"
        useraverageresult, randomresult = str(UserAverageMAE), str(RandomMAE)
        randomRecall = str(RandomRecall)
        randomPrecision = str(RandomPrecision)
        resfile.write("\User Average MAE "+useraverageresult+"\nRandom MAE"+randomresult+"\n\n")
        resfile.write("\Random Recall "+randomRecall+"\nRandom Precision "+randomPrecision+"\n\n")
        mae, recall, precision = str(AVG_MAE), str(AVG_RECALL), str(AVG_PRECISION)
        res = str(striteration+"\nFeatures MAE "+mae+" Recall "+recall + " Precision "+precision)
        resfile.write(res)
        print res

if __name__ == '__main__':
    main()
