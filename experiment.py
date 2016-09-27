import sqlite3
import recommender
import evaluation
import utils
import time

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

    NUM_USERS = 10 # constants.MAX_NUM_USERS
    RECOMMENDATION_LIST = 50 #increase at each iteration - important to measure Recall
    # ITEMS_TO_PREDICT = 2000 #constants.MAX_ITEMS_TO_PREDICT #list of all movies

    iterations = 1
    LIST_INCREASE = 25

    conn = sqlite3.connect('database.db')

    print "Starting Experiment... ", iterations, "iterations.", NUM_USERS, "users.", "recommender list size equal to", RECOMMENDATION_LIST, "."

    for i in range(iterations):

        print i, "iteration."

        Users = utils.selectRandomUsers(conn, NUM_USERS)
        MoviesToPredict = utils.selectTrainingMovies(conn)

        recall, precision = recommender.recommend(conn, Users, MoviesToPredict, recommender.lowlevel)
        print "Avg Recall", recall, "Avg Precision", precision
        recall, precision = recommender.recommend(conn, Users, MoviesToPredict, recommender.deep)
        print "Avg Recall", recall, "Avg Precision", precision

        # mae, recall, precision = recommender.recommend(conn, Users, MoviesToPredict, recommender.lowlevel, RECOMMENDATION_LIST)
        # print "MAE Features and Ratings ", mae, " Recall Features and Ratings ", recall, "Precision  Features and Ratings ", precision

        # mae, recall, precision = recommender.recommend(conn, Users, MoviesToPredict, recommender.deep,
        #                                                RECOMMENDATION_LIST)
        # print "MAE Features and Ratings ", mae, " Recall Features and Ratings ", recall, "Precision  Features and Ratings ", precision

        # ITEMS_TO_PREDICT += LIST_INCREASE

        # UserAverageMAE = evaluation.evaluateRandomMAE(conn, Users, MoviesToPredict, True)
        # RandomMAE = evaluation.evaluateRandomMAE(conn, Users, MoviesToPredict, False)

        # RandomRecall, RandomPrecision = evaluation.evaluateRandomPrecisionRecall(conn, Users, MoviesToPredict, RECOMMENDATION_LIST)
        # print "Random Precision", RandomPrecision, "Random Recall", RandomRecall

        # writeResults(iterations, LIST_INCREASE, i, UserAverageMAE, RandomMAE, AVG_MAE, AVG_RECALL, AVG_PRECISION, RandomRecall, RandomPrecision, NUM_USERS, ITEMS_TO_PREDICT)

        # print "User Average MAE ", (UserAverageMAE)
        # print "Random MAE ", (RandomMAE)

    conn.close()

def writeResults(iterations, LIST_INCREASE, i, UserAverageMAE, RandomMAE, AVG_MAE, AVG_RECALL, AVG_PRECISION, RandomRecall, RandomPrecision, NUM_USERS, LIMIT_ITEMS_TO_PREDICT):

    FILE_NAME = time.strftime('%d-%m-%Y')+'-imageNet-LSTM-128-'+str(NUM_USERS)+'users-'+str(LIMIT_ITEMS_TO_PREDICT)+'items-1iterations-'+str(iterations)+'Plus-List'+str(LIST_INCREASE)+'.txt'

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
