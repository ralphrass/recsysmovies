# necessary modules
import sqlite3
import utils
import recommender_classifier
import time
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process, Manager

# load random users and feature vectors
conn = sqlite3.connect('database.db')
Users = utils.selectRandomUsers(conn)
LOW_LEVEL_FEATURES, DEEP_FEATURES_RESNET, HYBRID_FEATURES_RESNET = utils.extract_features()
foo, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF = utils.extract_features('bof_128.bin')
# USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES = utils.extract_tfidf_features()

print len(Users)

user_profiles = recommender_classifier.build_user_profiles(conn, Users)


def run(user_profiles, N, feature_vector, feature_vector2=None):
    conn = sqlite3.connect('database.db')

    SumRecall, SumPrecision = 0, 0

    for user, profile in user_profiles.iteritems():

        if feature_vector2 is not None:
            if np.sum(feature_vector[user]) == 0:
                print "Blank user profile", user
                continue

        hits = 0

        predictions = recommender_classifier.get_predict_collaborative_filtering(conn, profile, feature_vector,
                                                                                 feature_vector2)
        # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)

        for elite_movie in profile['datasets']['elite_test']:

            if feature_vector is list and elite_movie[0] not in feature_vector:
                continue

            # Predict to the user movie and to random movies that the user did not rated
            # print predictions
            elite_prediction = recommender_classifier.get_prediction_elite(conn, elite_movie, profile, feature_vector,
                                                                           feature_vector2)
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
def experiment(N, res_ll, res_deep, res_hybrid, res_random, res_deep_bof, res_hybrid_bof):
    global user_profiles, LOW_LEVEL_FEATURES, DEEP_FEATURES_RESNET, HYBRID_FEATURES_RESNET, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF

    result = {}
    start = time.time()

    # Tag-based
    # p_t, r_t = run(user_profiles, N, USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES)
    # print "Tag-based Recall", r_t, "Tag-based Precision", p_t, "For iteration with", N

    # LOW LEVEL FEATURES check precision, recall and mae
    p_l, r_l = run(user_profiles, N, LOW_LEVEL_FEATURES)
    res_ll[N] = {'ll': {'recall': r_l, 'precision': p_l}}
    print "Low-Level Recall", r_l, "Low-Level Precision", p_l, "For iteration with", N

    # end = time.time()
    # print "Execution time", (end - start)

    # start = time.time()
    # DEEP FEATURES - RESNET
    p_d, r_d = run(user_profiles, N, DEEP_FEATURES_RESNET)
    res_deep[N] = {'deep_resnet': {'recall': r_d, 'precision': p_d}}
    print "Deep Resnet Recall", r_d, "Deep Resnet Precision", p_d, "For iteration with", N

    # HYBRID - RESNET
    p_h, r_h = run(user_profiles, N, HYBRID_FEATURES_RESNET)
    res_hybrid[N] = {'hybrid_resnet': {'recall': r_h, 'precision': p_h}}
    print "Hybrid Resnet Recall", r_h, "Hybrid Resnet Precision", p_h, "For iteration with", N

    # DEEP FEATURES - BOF
    p_d, r_d = run(user_profiles, N, DEEP_FEATURES_BOF)
    res_deep_bof[N] = {'deep_bof': {'recall': r_d, 'precision': p_d}}
    print "Deep BOF Recall", r_d, "Deep BOF Precision", p_d, "For iteration with", N

    # HYBRID - BOF
    p_h, r_h = run(user_profiles, N, HYBRID_FEATURES_BOF)
    res_hybrid_bof[N] = {'hybrid_bof': {'recall': r_h, 'precision': p_h}}
    print "Hybrid BOF Recall", r_h, "Hybrid BOF Precision", p_h, "For iteration with", N

    p, r, mae = recommender_classifier.recommend_random(user_profiles, N)
    res_random[N] = {'random': {'recall': r, 'precision': p}}
    print "Random Recall", r, "Random Precision", p, "Random MAE", mae, "For iteration with", N

    # return_dict[N] = {'ll': {'recall': r_l, 'precision': p_l}, 'deep': {'recall': r_d, 'precision': p_d}, 'hybrid': {'recall': r_h, 'precision': p_h}, 'random': {'recall': r, 'precision': p}}
    end = time.time()
    print "Execution time", (end - start)

#     result = {'ll': {'recall': r_l, 'precision': p_l}, 'deep': {'recall': r_d, 'precision': p_d}, 'random': {'recall': r, 'precision': p}}


iterations = range(1, 3)

# experiment(1)
manager = Manager()
res_ll = manager.dict()
res_deep = manager.dict()
res_hybrid = manager.dict()
res_deep_bof = manager.dict()
res_hybrid_bof = manager.dict()
res_random = manager.dict()

jobs = []
for num in iterations:
    p = Process(target=experiment, args=(num,res_ll,res_deep,res_hybrid,res_random,res_deep_bof,res_hybrid_bof))
    jobs.append(p)
    p.start()

for proc in jobs:
    proc.join()
# print return_dict.values()

# p = Pool(5)
# print(p.map(experiment, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]))


low_level_recall = [item['ll']['recall'] for item in res_ll.values()]
deep_recall = [item['deep_resnet']['recall'] for item in res_deep.values()]
hybrid_recall = [item['hybrid_resnet']['recall'] for item in res_hybrid.values()]
deep_bof_recall = [item['deep_bof']['recall'] for item in res_deep_bof.values()]
hybrid_bof_recall = [item['hybrid_bof']['recall'] for item in res_hybrid_bof.values()]
random_recall = [item['random']['recall'] for item in res_random.values()]

# print low_level_recall
# print deep_recall
# print low_level_recall

# for key, value in low_level_recall.items():
#      print "Entry", key, value


plt.plot(iterations, low_level_recall, 'r-', iterations, deep_recall, 'g-', iterations, hybrid_recall, 'b-', iterations, random_recall, 'y-')
plt.ylabel('Recall')
plt.xlabel('Iterations')
plt.savefig('results.png')
# plt.show()

# fig, ax = plt.subplots()

# # Be sure to only pick integer tick locations.
# for axis in [ax.xaxis, ax.yaxis]:
#     axis.set_major_locator(ticker.MaxNLocator(integer=True))

# # Plot anything (note the non-integer min-max values)...
# x = np.linspace(-0.1, np.pi, 100)
# ax.plot(range(1,6), low_level_recall, 'r--', range(1,6), deep_recall, 'g--', range(1,6), hybrid_recall, 'b--', range(1,6), random_recall, 'y--')

# # Just for appearance's sake
# ax.margins(0.05)
# ax.axis('tight')
# fig.tight_layout()

# plt.show()
