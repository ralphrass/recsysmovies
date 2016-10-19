import sqlite3
import utils
import recommender
import time
from multiprocessing import Process, Manager

start = time.time()

# load random users and feature vectors
conn = sqlite3.connect('database.db')

Users = utils.selectRandomUsers(conn, 0, 850)

LOW_LEVEL_FEATURES, DEEP_FEATURES_RESNET, HYBRID_FEATURES_RESNET = utils.extract_features()
foo, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF = utils.extract_features('bof_128.bin')
# USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES = utils.extract_tfidf_features()

print len(Users)

similarity_matrices = utils.get_similarity_matrices()
feature_vectors = [LOW_LEVEL_FEATURES, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF]
strategies = {0: ('low-level-random', 'low-level-elite'), 1: ('deep-random', 'deep-elite'), 2: ('hybrid-random', 'hybrid-elite')}

start = time.time()

user_profiles = recommender.build_user_profiles(Users, feature_vectors, strategies, similarity_matrices)

print (time.time() - start), "seconds"


def experiment(N, user_profiles):
    global LOW_LEVEL_FEATURES, DEEP_FEATURES_RESNET, HYBRID_FEATURES_RESNET, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF

    result = {}
    # start = time.time()

    # Tag-based
    # p_t, r_t = run(user_profiles, N, USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES)
    # print "Tag-based Recall", r_t, "Tag-based Precision", p_t, "For iteration with", N

    # LOW LEVEL FEATURES check precision, recall and mae
    p_l, r_l = recommender.run(user_profiles, N, LOW_LEVEL_FEATURES, 'low-level')
    # res_ll[N] = {'ll': {'recall': r_l, 'precision': p_l}}
    print "Low-Level Recall", r_l, "Low-Level Precision", p_l, "For iteration with", N

    # end = time.time()
    # print "Execution time", (end - start)

    # start = time.time()
    # DEEP FEATURES - RESNET
    # p_d, r_d = recommender.run(user_profiles, N, DEEP_FEATURES_RESNET, 'deep')
    # # res_deep[N] = {'deep_resnet': {'recall': r_d, 'precision': p_d}}
    # print "Deep Resnet Recall", r_d, "Deep Resnet Precision", p_d, "For iteration with", N
    # #
    # # # HYBRID - RESNET
    # p_h, r_h = recommender.run(user_profiles, N, HYBRID_FEATURES_RESNET)
    # # res_hybrid[N] = {'hybrid_resnet': {'recall': r_h, 'precision': p_h}}
    # print "Hybrid Resnet Recall", r_h, "Hybrid Resnet Precision", p_h, "For iteration with", N


    # DEEP FEATURES - BOF
    p_d, r_d = recommender.run(user_profiles, N, DEEP_FEATURES_BOF, 'deep')
    # res_deep_bof[N] = {'deep_bof': {'recall': r_d, 'precision': p_d}}
    print "Deep BOF Recall", r_d, "Deep BOF Precision", p_d, "For iteration with", N
    # #
    # HYBRID - BOF
    p_h, r_h = recommender.run(user_profiles, N, HYBRID_FEATURES_BOF, 'hybrid')
    # res_hybrid_bof[N] = {'hybrid_bof': {'recall': r_h, 'precision': p_h}}
    print "Hybrid BOF Recall", r_h, "Hybrid BOF Precision", p_h, "For iteration with", N

    p, r = recommender.run(user_profiles, N, None, 'random')
    # res_random[N] = {'random': {'recall': r, 'precision': p}}
    print "Random Recall", r, "Random Precision", p, "For iteration with", N

    # p, r = recommender.run(user_profiles, N, None, 'tfidf')
    # res_random[N] = {'random': {'recall': r, 'precision': p}}
    # print "TFIDF Recall", r, "TFIDF Precision", p, "For iteration with", N

    # return_dict[N] = {'ll': {'recall': r_l, 'precision': p_l}, 'deep': {'recall': r_d, 'precision': p_d}, 'hybrid': {'recall': r_h, 'precision': p_h}, 'random': {'recall': r, 'precision': p}}
    # end = time.time()
    # print "Execution time", (end - start)

#     result = {'ll': {'recall': r_l, 'precision': p_l}, 'deep': {'recall': r_d, 'precision': p_d}, 'random': {'recall': r, 'precision': p}}

iterations = range(1, 21)

jobs = []
for index in iterations:
    p = Process(target=experiment, args=(index, user_profiles))
    jobs.append(p)
    p.start()

for proc in jobs:
    proc.join()

end = time.time()
print "Execution time", (end - start)
