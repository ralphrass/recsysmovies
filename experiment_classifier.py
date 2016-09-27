import sqlite3
import recommender_classifier
import evaluation
import utils
import time
from opening_feat import load_features

def main():

    RECOMMENDATION_LIST = 10 #increase at each iteration - important to measure Recall
    iterations = 5
    LIST_INCREASE = 5

    conn = sqlite3.connect('database.db')

    DEEP_FEATURES = load_features('resnet_152_lstm_128.dct')
    LOW_LEVEL_FEATURES = load_features('low_level_dict.bin')

    print "Starting Experiment... ", iterations, "iterations.", "recommender list size equal to", RECOMMENDATION_LIST, "."
    avgrecall_lowlevel = 0
    avgprecision_lowlevel = 0
    avgrecall_deep = 0
    avgprecision_deep = 0
    avgrecall_hybrid = 0
    avgprecision_hybrid = 0

    for i in range(iterations):

        print i, "iteration."

        Users = utils.selectRandomUsers(conn)
        # MoviesToPredict = utils.selectTrainingMovies(conn)

        recall, precision = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, LOW_LEVEL_FEATURES)
        print "Low-Level Recall", recall, "Low-Level Precision", precision
        avgrecall_lowlevel += recall
        avgprecision_lowlevel += precision

        recall, precision = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, DEEP_FEATURES)
        print "Deep Recall", recall, "Deep Precision", precision
        avgrecall_deep += recall
        avgprecision_deep += precision
        #
        # recall, precision = recommender.recommend(conn, Users, RECOMMENDATION_LIST, recommender.hybrid)
        # print "Hybrid Recall", recall, "Hybrid Precision", precision
        # avgrecall_hybrid += recall
        # avgprecision_hybrid += precision

        RECOMMENDATION_LIST += LIST_INCREASE

    print "AVG FULL Low-Level Recall ", (avgrecall_lowlevel / iterations)
    print "AVG FULL Low-Level Precision ", (avgprecision_lowlevel / iterations)
    print "AVG FULL Deep Recall ", (avgrecall_deep / iterations)
    print "AVG FULL Deep Precision", (avgprecision_deep / iterations)
    print "AVG FULL Hybrid Recall ", (avgrecall_hybrid / iterations)
    print "AVG FULL Hybrid Precision ", (avgprecision_hybrid / iterations)

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
