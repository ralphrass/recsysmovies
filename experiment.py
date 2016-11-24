import sqlite3
import utils
import recommender
import time
import pandas as pd
import gc
from multiprocessing import Process, Manager
import random
import evaluation

iterations = range(1, 16)

start = time.time()

# load random users and feature vectors
conn = sqlite3.connect('database.db')

batch = 1
print "batch", batch+1

# 85040 is the full set size (4252 is 20 iterations)
Users = utils.selectRandomUsers(conn, 4252*batch, 4252)

# LOW_LEVEL_FEATURES, DEEP_FEATURES_RESNET, HYBRID_FEATURES_RESNET = utils.extract_features()
LOW_LEVEL_FEATURES, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF = utils.extract_features('bof_128.bin')
# USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES = utils.extract_tfidf_features()

print len(Users)

similarity_matrices = utils.get_similarity_matrices()
feature_vectors = [LOW_LEVEL_FEATURES, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF]
strategies = {0: ('low-level-random', 'low-level-elite', 'low-level-garbage'),
              1: ('deep-random', 'deep-elite', 'deep-garbage'),
              2: ('hybrid-random', 'hybrid-elite', 'hybrid-garbage')}

_ratings = pd.read_sql("SELECT userid, SUM(rating)/COUNT(rating) AS average "
                       "FROM movielens_rating GROUP BY userid ORDER BY userid", conn, columns=['average'],
                       index_col='userID')
_ratings_by_movie = pd.read_sql("SELECT movielensid, SUM(rating)/COUNT(rating) AS average "
                                "FROM movielens_rating GROUP BY movielensid ORDER BY movielensid", conn,
                                columns=['average'], index_col='movielensID')
_global_average = _ratings['average'].mean()

start = time.time()

user_profiles = recommender.build_user_profile(Users, feature_vectors, similarity_matrices, _ratings, _ratings_by_movie,
                                               _global_average)
RandomUsers = random.sample(user_profiles, 3)
print RandomUsers

for user in RandomUsers:
    print "User", user
    print "Relevant Movies", user_profiles[user]['datasets']['relevant_movies']
    print "LL Predicitons", user_profiles[user]['predictions']['low-level']
    print "Deep Predicitons", user_profiles[user]['predictions']['deep']

# print user_profiles

print time.time()
print "Profiles buit"
# _ratings = None
# _ratings_by_movie = None
# gc.collect()
# print "gabage collected"

print (time.time() - start), "seconds"


def experiment(N, user_profiles):
    global LOW_LEVEL_FEATURES, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF, _ratings, _global_average, _ratings_by_movie
    # Tag-based
    # p_t, r_t = run(user_profiles, N, USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES)
    # print "Tag-based Recall", r_t, "Tag-based Precision", p_t, "For iteration with", N
    # LOW LEVEL FEATURES check precision, recall and mae
    # p_l, r_l, m_l, s_l = recommender.run(user_profiles, N, LOW_LEVEL_FEATURES, 'low-level')
    p, r, d = evaluation.evaluate(user_profiles, N, 'low-level', similarity_matrices[0])
    print "Low-Level Recall", r, "Low-Level Precision", p, "LL Diversity", d, "For iteration with", N

    # DEEP FEATURES - BOF
    # p_d, r_d, m_d, s_d = recommender.run(user_profiles, N, DEEP_FEATURES_BOF, 'deep')
    p, r, d = evaluation.evaluate(user_profiles, N, 'deep', similarity_matrices[1])
    print "Deep BOF Recall", r, "Deep BOF Precision", p, "Deep Diversity", d, "For iteration with", N

    # p_h, r_h, m_h, s_h = recommender.run(user_profiles, N, HYBRID_FEATURES_BOF, 'hybrid')
    p, r, d = evaluation.evaluate(user_profiles, N, 'hybrid', similarity_matrices[2])
    print "Hybrid BOF Recall", r, "Hybrid BOF Precision", p, "Hybrid Diversity", d, "For iteration with", N

    # p, r, m, s = recommender.run(user_profiles, N, None, 'random')
    p, r, d = evaluation.evaluate(user_profiles, N, 'random', None)
    print "Random Recall", r, "Random Precision", p, "Random Diversity", d, "For iteration with", N

    # if N == 1:
    #     print "LL MAE", m_l
    #     print "Deep MAE", m_d
    #     print "Hybrid MAE", m_h
    #     print "Random MAE", m


jobs = []
for index in iterations:
    p = Process(target=experiment, args=(index, user_profiles))
    jobs.append(p)
    p.start()

for proc in jobs:
    proc.join()

end = time.time()
print "Execution time", (end - start)
