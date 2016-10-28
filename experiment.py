import sqlite3
import utils
import recommender
import time
import pandas as pd
import gc
from multiprocessing import Process, Manager

iterations = range(1, 16)

start = time.time()

# load random users and feature vectors
conn = sqlite3.connect('database.db')

batch = 7
print "batch", batch+1

# 85040 is the full set size (4252 is 20 iterations)
Users = utils.selectRandomUsers(conn, 4252*batch, 4252)

LOW_LEVEL_FEATURES, DEEP_FEATURES_RESNET, HYBRID_FEATURES_RESNET = utils.extract_features()
foo, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF = utils.extract_features('bof_128.bin')
# USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES = utils.extract_tfidf_features()

print len(Users)

similarity_matrices = utils.get_similarity_matrices()
feature_vectors = [LOW_LEVEL_FEATURES, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF]
strategies = {0: ('low-level-random', 'low-level-elite'), 1: ('deep-random', 'deep-elite'), 2: ('hybrid-random', 'hybrid-elite')}

_ratings = pd.read_sql("SELECT userid, SUM(rating)/COUNT(rating) AS average "
                       "FROM movielens_rating GROUP BY userid ORDER BY userid", conn, columns=['average'],
                       index_col='userID')
_ratings_by_movie = pd.read_sql("SELECT movielensid, SUM(rating)/COUNT(rating) AS average "
                                "FROM movielens_rating GROUP BY movielensid ORDER BY movielensid", conn,
                                columns=['average'], index_col='movielensID')
_global_average = _ratings['average'].mean()

start = time.time()

user_profiles = recommender.build_user_profiles(Users, feature_vectors, strategies, similarity_matrices, _ratings,
                                                _ratings_by_movie, _global_average)

print time.time()
print "Profiles buit"
# _ratings = None
# _ratings_by_movie = None
# gc.collect()
# print "gabage collected"

print (time.time() - start), "seconds"


def experiment(N, user_profiles):
    global LOW_LEVEL_FEATURES, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF, _ratings, _global_average, _ratings_by_movie

    # result = {}
    # start = time.time()

    # Tag-based
    # p_t, r_t = run(user_profiles, N, USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES)
    # print "Tag-based Recall", r_t, "Tag-based Precision", p_t, "For iteration with", N

    # LOW LEVEL FEATURES check precision, recall and mae
    p_l, r_l, m_l = recommender.run(user_profiles, N, LOW_LEVEL_FEATURES, 'low-level')
    # res_ll[N] = {'ll': {'recall': r_l, 'precision': p_l}}
    print "Low-Level Recall", r_l, "Low-Level Precision", p_l, "LL MAE", m_l, "For iteration with", N

    # DEEP FEATURES - BOF
    p_d, r_d, m_d = recommender.run(user_profiles, N, DEEP_FEATURES_BOF, 'deep')
    # res_deep_bof[N] = {'deep_bof': {'recall': r_d, 'precision': p_d}}
    print "Deep BOF Recall", r_d, "Deep BOF Precision", p_d, "LL MAE", m_d, "For iteration with", N
    # #
    # HYBRID - BOF
    p_h, r_h, m_h = recommender.run(user_profiles, N, HYBRID_FEATURES_BOF, 'hybrid')
    # res_hybrid_bof[N] = {'hybrid_bof': {'recall': r_h, 'precision': p_h}}
    print "Hybrid BOF Recall", r_h, "Hybrid BOF Precision", p_h, "LL MAE", m_h, "For iteration with", N

    p, r, m = recommender.run(user_profiles, N, None, 'random')
    # res_random[N] = {'random': {'recall': r, 'precision': p}}
    print "Random Recall", r, "Random Precision", p, "LL MAE", m, "For iteration with", N

    # p, r = recommender.run(user_profiles, N, None, 'tfidf')
    # res_random[N] = {'random': {'recall': r, 'precision': p}}
    # print "TFIDF Recall", r, "TFIDF Precision", p, "For iteration with", N


jobs = []
for index in iterations:
    p = Process(target=experiment, args=(index, user_profiles))
    jobs.append(p)
    p.start()

for proc in jobs:
    proc.join()

end = time.time()
print "Execution time", (end - start)
