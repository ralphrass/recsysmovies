import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
np.set_printoptions(threshold=np.inf)

conn = sqlite3.connect('../database.db')

# select users and contrast user-item profiles

sql_user = "SELECT userid, tfidfprofile " \
      "FROM movielens_user_tfidf_profile "

sql_movies = "SELECT mm.title, m.tfidfprofile " \
             "FROM movielens_movie_tfidf_profile m " \
             "JOIN movielens_movie mm ON mm.movielensid = m.movielensid " \
             "JOIN movielens_test_dataset mtd ON mtd.movielensid = m.movielensid "

c = conn.cursor()
c.execute(sql_user)
user_profiles = c.fetchall()

c = conn.cursor()
c.execute(sql_movies)
movie_profiles = [(x[0], np.array(x[1])) for x in c.fetchall()]

users = {}

for user_profile in user_profiles:
    user_tfidf = user_profile[1]
    userid = user_profile[0]

    user_recommendations = []

    for movie in movie_profiles:
        # movie_tfidf = np.array(movie[1])
        # movie_tfidf = movie[1].reshape(1, -1)
        # user_tfidf = user_tfidf.reshape(1, -1)

        print user_profile[1]

        # print movie_tfidf.astype(np.float), type(movie_tfidf)
        exit()

        sim = cosine_similarity(movie_tfidf, user_tfidf)
        user_recommendations.append((movie[0], sim))

    users[userid] = user_recommendations

    print users
    exit()

kMostSimilar = sorted(users[userid], key=lambda tup: tup[1], reverse=True)[:30]
print kMostSimilar