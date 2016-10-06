import recommender_classifier
import evaluation
import utils
import time
from opening_feat import load_features
from sklearn import preprocessing
import numpy as np
import itertools as it
from multiprocessing import Pool
# low_level_features = load_features('low_level_dict.bin') # normalize
import sqlite3
import utils
import recommender_classifier
import time
from sklearn import svm
from sklearn.metrics import mean_absolute_error
from multiprocessing import Pool

# conn = sqlite3.connect('database.db')
# Users = utils.selectRandomUsers(conn)


def run(user_profiles, N, feature_vector):
    conn = sqlite3.connect('database.db')

    SumRecall, SumPrecision = 0, 0

    for user, profile in user_profiles.iteritems():

        hits = 0

        predictions = recommender_classifier.get_predict_collaborative_filtering(conn, profile, feature_vector)
        # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)

        for elite_movie in profile['datasets']['elite_test']:

            if feature_vector is list and elite_movie[0] not in feature_vector:
                continue

            # Predict to the user movie and to random movies that the user did not rated
            # print predictions
            elite_prediction = recommender_classifier.get_prediction_elite(conn, elite_movie, profile, feature_vector)
            all_predictions = predictions[:]
            all_predictions.append(elite_prediction)

            # print "Elite Movie", elite_movie, elite_prediction

            hits += recommender_classifier.count_hit(all_predictions, elite_movie, N)
        try:
            recall = hits / float(len(profile['datasets']['elite_test']))
            SumRecall += recall
            SumPrecision += (recall / float(N))
        except ZeroDivisionError:
            continue
            # print "Size is", len(predictions)
            # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)

    size = len(user_profiles)
    avgRecall = utils.evaluateAverage(SumRecall, size)
    avgPrecision = utils.evaluateAverage(SumPrecision, size)

    return avgPrecision, avgRecall


# def experiment(N, user_profiles_low_level, LOW_LEVEL_FEATURES, user_profiles_deep, DEEP_FEATURES):
def experiment(N):
    global user_profiles, LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES

    result = {}
    start = time.time()

    # COLLABORATIVE FILTERING
    # p_c, r_c = run(user_profiles, N, None)
    # print "CF Recall", r_c, "CF Precision", p_c, "For iteration with", N, "\n\n"
    #     result[N] = {'cf': {'recall': r_c, 'precision': p_c}}

    # LOW LEVEL FEATURES check precision, recall and mae
    p_l, r_l = run(user_profiles, N, LOW_LEVEL_FEATURES)
    print "Low-Level Recall", r_l, "Low-Level Precision", p_l, "For iteration with", N

    end = time.time()
    print "Execution time", (end - start)
    #     result[N] = {'ll': {'recall': r_l, 'precision': p_l}}

    start = time.time()
    # DEEP FEATURES check precision, recall and mae
    p_d, r_d = run(user_profiles, N, DEEP_FEATURES)
    print "Deep Recall", r_d, "Deep Precision", p_d, "For iteration with", N
    end = time.time()
    print "Execution time", (end - start)
    #     result[N] = {'deep': {'recall': r_d, 'precision': p_d}}

    # HYBRID
    #     p_d, r_d = run(user_profiles_deep, N, HYBRID_FEATURES)
    #     p_d, r_d = run(user_profiles, N, HYBRID_FEATURES)
    #     print "Hybrid Recall", r_d, "Hybrid Precision", p_d, "For iteration with", N, "\n\n"
    #     result[N] = {'hybrid': {'recall': r_d, 'precision': p_d}}

    p, r, mae = recommender_classifier.recommend_random(user_profiles, N)
    print "Random Recall", r, "Random Precision", p, "Random MAE", mae, "For iteration with", N, "\n\n"


# load random users and feature vectors
conn = sqlite3.connect('database.db')
Users = utils.selectRandomUsers(conn)
LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES = utils.extract_features()

print len(Users)

user_profiles = recommender_classifier.build_user_profiles(conn, Users)

p = Pool(1)
print(p.map(experiment, [1]))



print "Full users dataset contains", len(Users), "users"

def extract_features():
    DEEP_FEATURES = load_features('resnet_152_lstm_128.dct')
    arr = np.array([x[1] for x in DEEP_FEATURES.iteritems()])
    # normalized_ll_features = preprocessing.normalize(arr)
    # DEEP_FEATURES = {k: v for k, v in it.izip(DEEP_FEATURES.keys(), normalized_ll_features)}

    scaler = preprocessing.StandardScaler().fit(arr)
    std = scaler.transform(arr)
    # DEEP_FEATURES = {k: v for k, v in it.izip(DEEP_FEATURES.keys(), std)}

    LOW_LEVEL_FEATURES = load_features('low_level_dict.bin')
    arr = np.array([x[1] for x in LOW_LEVEL_FEATURES.iteritems()])
    # normalized_ll_features = preprocessing.normalize(arr)
    # LOW_LEVEL_FEATURES = {k: v for k, v in it.izip(LOW_LEVEL_FEATURES.keys(), normalized_ll_features)}

    scaler = preprocessing.StandardScaler().fit(arr)
    std = scaler.transform(arr)
    LOW_LEVEL_FEATURES = {k: v for k, v in it.izip(LOW_LEVEL_FEATURES.keys(), std)}

    HYBRID_FEATURES = {}

    for k in DEEP_FEATURES.iterkeys():
        try:
            HYBRID_FEATURES[k] = np.append(DEEP_FEATURES[k], LOW_LEVEL_FEATURES[k])
        except KeyError:
            # HYBRID_FEATURES[k] = DEEP_FEATURES[k]
            continue

    return LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES


def main():

    # RECOMMENDATION_LIST = 1 #increase at each iteration - important to measure Recall
    # iterations = 10
    # LIST_INCREASE = 1
    #
    # conn = sqlite3.connect('database.db')
    #
    # DEEP_FEATURES = load_features('resnet_152_lstm_128.dct')
    # arr = np.array([x[1] for x in DEEP_FEATURES.iteritems()])
    # # normalized_ll_features = preprocessing.normalize(arr)
    # # DEEP_FEATURES = {k: v for k, v in it.izip(DEEP_FEATURES.keys(), normalized_ll_features)}
    #
    # scaler = preprocessing.StandardScaler().fit(arr)
    # std = scaler.transform(arr)
    # DEEP_FEATURES = {k: v for k, v in it.izip(DEEP_FEATURES.keys(), std)}
    #
    # LOW_LEVEL_FEATURES = load_features('low_level_dict.bin')
    # arr = np.array([x[1] for x in LOW_LEVEL_FEATURES.iteritems()])
    # # normalized_ll_features = preprocessing.normalize(arr)
    # # LOW_LEVEL_FEATURES = {k: v for k, v in it.izip(LOW_LEVEL_FEATURES.keys(), normalized_ll_features)}
    #
    # scaler = preprocessing.StandardScaler().fit(arr)
    # std = scaler.transform(arr)
    # LOW_LEVEL_FEATURES = {k: v for k, v in it.izip(LOW_LEVEL_FEATURES.keys(), std)}
    #
    # HYBRID_FEATURES = {}
    #
    # for k in DEEP_FEATURES.iterkeys():
    #     try:
    #         HYBRID_FEATURES[k] = np.append(DEEP_FEATURES[k], LOW_LEVEL_FEATURES[k])
    #     except KeyError:
    #         # HYBRID_FEATURES[k] = DEEP_FEATURES[k]
    #         continue

    # print "Starting Experiment... ", iterations, "iterations.", "recommender list size equal to", RECOMMENDATION_LIST, "."
    avgrecall_lowlevel = 0
    avgprecision_lowlevel = 0
    avgmae_lowlevel = 0
    avgrecall_deep = 0
    avgprecision_deep = 0
    avgmae_deep = 0
    avgrecall_hybrid = 0
    avgprecision_hybrid = 0
    avgmae_hybrid = 0
    avgrecall_random = 0
    avgprecision_random = 0

    randomrecall = 0
    randomprecision = 0

    # Users = utils.selectRandomUsers(conn)

    p = Pool(5)
    print(p.map(run, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    # p = Pool(1)
    # print(p.map(run, [1]))

    # for i in range(iterations):
    #
    #     print i, "iteration."
    #
    #     # MoviesToPredict = utils.selectTrainingMovies(conn)
    #
    #     precision, recall, mae = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, LOW_LEVEL_FEATURES)
    #     print "Low-Level Recall", recall, "Low-Level Precision", precision, "Low-Level MAE", mae
    #     avgrecall_lowlevel += recall
    #     avgprecision_lowlevel += precision
    #     # avgmae_lowlevel += mae
    #
    #     precision, recall, mae = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, DEEP_FEATURES)
    #     print "Deep Recall", recall, "Deep Precision", precision, "Deep MAE", mae
    #     avgrecall_deep += recall
    #     avgprecision_deep += precision
    #     # avgmae_deep += mae
    #
    #     precision, recall, mae = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, HYBRID_FEATURES)
    #     print "Hybrid Recall", recall, "Hybrid Precision", precision, "Hybrid MAE", mae
    #     avgrecall_hybrid += recall
    #     avgprecision_hybrid += precision
    #     # avgmae_hybrid += mae
    #
    #     precision, recall = recommender_classifier.recommend_random(conn, Users, RECOMMENDATION_LIST)
    #     print "Random Recall", recall, "Random Precision", precision
    #     avgrecall_random += recall
    #     avgprecision_random += precision
    #
    #     RECOMMENDATION_LIST += LIST_INCREASE
    #
    # print "AVG FULL Low-Level Recall ", (avgrecall_lowlevel / iterations)
    # print "AVG FULL Low-Level Precision ", (avgprecision_lowlevel / iterations)
    # # print "AVG FULL Low-Level MAE ", (avgmae_lowlevel / iterations)
    # print "AVG FULL Deep Recall ", (avgrecall_deep / iterations)
    # print "AVG FULL Deep Precision", (avgprecision_deep / iterations)
    # # print "AVG FULL Deep MAE ", (avgmae_deep / iterations)
    # print "AVG FULL Hybrid Recall ", (avgrecall_hybrid / iterations)
    # print "AVG FULL Hybrid Precision ", (avgprecision_hybrid / iterations)
    # # print "AVG FULL Hybrid MAE ", (avgmae_hybrid / iterations)
    # print "AVG FULL Random Recall ", (avgrecall_random / iterations)
    # print "AVG FULL Random Precision ", (avgprecision_random / iterations)

    # conn.close()


def run(RECOMMENDATION_LIST):

    global Users

    conn = sqlite3.connect('database.db')

    LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES = extract_features()

    print RECOMMENDATION_LIST, "iteration."

    precision, recall, mae = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, LOW_LEVEL_FEATURES)
    print "Low-Level Recall", recall, "Low-Level Precision", precision, "For iteration with", RECOMMENDATION_LIST
    # avgrecall_lowlevel = recall
    # avgprecision_lowlevel = precision

    precision, recall, mae = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, DEEP_FEATURES)
    print "Deep Recall", recall, "Deep Precision", precision, "For iteration with", RECOMMENDATION_LIST
    # avgrecall_deep = recall
    # avgprecision_deep = precision

    precision, recall, mae = recommender_classifier.recommend(conn, Users, RECOMMENDATION_LIST, HYBRID_FEATURES)
    print "Hybrid Recall", recall, "Hybrid Precision", precision, "For iteration with", RECOMMENDATION_LIST
    # avgrecall_hybrid = recall
    # avgprecision_hybrid = precision

    precision, recall = recommender_classifier.recommend_random(conn, Users, RECOMMENDATION_LIST)
    print "Random Recall", recall, "Random Precision",  precision, "For iteration with", RECOMMENDATION_LIST
    # avgrecall_random = recall
    # avgprecision_random = precision

    # print "AVG FULL Low-Level Recall ", avgrecall_lowlevel
    # print "AVG FULL Low-Level Precision ", avgprecision_lowlevel
    # # print "AVG FULL Low-Level MAE ", (avgmae_lowlevel / iterations)
    # print "AVG FULL Deep Recall ", avgrecall_deep
    # print "AVG FULL Deep Precision", avgprecision_deep
    # # print "AVG FULL Deep MAE ", (avgmae_deep / iterations)
    # print "AVG FULL Hybrid Recall ", avgrecall_hybrid
    # print "AVG FULL Hybrid Precision ", avgprecision_hybrid
    # # print "AVG FULL Hybrid MAE ", (avgmae_hybrid / iterations)
    # print "AVG FULL Random Recall ", avgrecall_random
    # print "AVG FULL Random Precision ", avgprecision_random



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

# if __name__ == '__main__':
#     main()


