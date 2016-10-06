import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
np.set_printoptions(threshold=np.inf)
import random
import opening_feat as of

user_features = of.load_features('../users_tfidf_profile.bin')
movie_features = of.load_features('../movies_tfidf_profile.bin')

print user_features[121]
# print movie_features[47]

exit()

conn = sqlite3.connect('../database.db')

# I deleted all the movie tags that were applied less than 50 times

# select users and contrast user-item profiles

# sql_user = "SELECT userid, tfidfprofile " \
#       "FROM movielens_user_tfidf_profile "

sql_user = "SELECT DISTINCT r.userid FROM movielens_rating r " \
           "JOIN movielens_tag t ON t.movielensid = r.movielensID AND t.userid = r.userid "

# sql_movies = "SELECT mm.title, m.tfidfprofile " \
#              "FROM movielens_movie_tfidf_profile m " \
#              "JOIN movielens_movie mm ON mm.movielensid = m.movielensid " \
#              "JOIN movielens_test_dataset mtd ON mtd.movielensid = m.movielensid "

sql_movies = "SELECT DISTINCT m.movielensid FROM movielens_movie m " \
             "JOIN movielens_tag t ON t.movielensid = m.movielensid"

c = conn.cursor()
c.execute(sql_user)
# user_profiles = [(x[0], np.array(x[1])) for x in c.fetchall()]
user_profiles = c.fetchall()

print len(user_profiles)

c = conn.cursor()
c.execute(sql_movies)
# movie_profiles = [(x[0], np.array(x[1])) for x in c.fetchall()]
movie_profiles = c.fetchall()

print len(movie_profiles)

users = {}

TOTAL_USERS = float(4897)
TOTAL_MOVIES = float(2903)

sql_all_tags = "SELECT DISTINCT tag FROM movielens_tag"
c = conn.cursor()
c.execute(sql_all_tags)
all_tags = [str(x[0]) for x in c.fetchall()]


def getUsersByTag(conn, tag):
    sqluserbytag = "SELECT COUNT(DISTINCT userid) FROM movielens_tag WHERE tag LIKE ?"
    c = conn.cursor()
    c.execute(sqluserbytag, (tag,))
    totalTags = c.fetchone()[0]

    return totalTags


def get_user_profile(user):

    global conn, all_tags

    sql_tags = "SELECT t.tag, COUNT(*) " \
               "FROM movielens_tag t " \
               "JOIN movielens_rating r ON r.userid = t.userid AND r.movielensid = t.movielensid " \
               "WHERE t.userid = ? AND r.rating > 4 " \
               "GROUP BY t.tag"

    c = conn.cursor()
    c.execute(sql_tags, (user,))
    tags = c.fetchall()
    training_set = random.sample(tags, int(len(tags) * 0.8))
    # print tags

    user_profile_tfidf = np.zeros(len(all_tags), dtype=np.float)

    for tag in training_set:
        tf = float(tag[1])
        idf = float(np.log(TOTAL_USERS / getUsersByTag(conn, tag[0])))
        tfidf = float(tf * idf)
        user_profile_tfidf[all_tags.index(str(tag[0]))] = tfidf

    return user_profile_tfidf


def get_movie_profile(movie):

    sql_tags = "SELECT tag, COUNT(*) FROM movielens_tag t " \
               "JOIN movielens_rating r ON r.userid = t.userid AND r.movielensid = t.movielensid " \
               "WHERE t.movielensid = ? AND r.rating > 4 " \
               "GROUP BY tag"

    c = conn.cursor()
    c.execute(sql_tags, (movie,))
    tags = c.fetchall()

    movie_profile = np.zeros(len(all_tags), dtype=np.float)

    for tag in tags:
        tf = float(tag[1])
        idf = float(np.log(TOTAL_MOVIES / getUsersByTag(conn, tag[0])))
        tfidf = float(tf * idf)
        movie_profile[all_tags.index(str(tag[0]))] = tfidf

    return movie_profile

for user_profile in user_profiles:

    user_tfidf = get_user_profile(user_profile[0])
    if np.sum(user_tfidf) == 0:
        continue
    userid = user_profile[0]

    print userid

    user_recommendations = []

    for movie in movie_profiles:

        movie_tfidf = get_movie_profile(movie[0])
        # movie_tfidf = movie[1].reshape(1, -1)
        # user_tfidf = user_tfidf.reshape(1, -1)

        # print user_tfidf
        # print movie_tfidf

        sim = cosine_similarity([movie_tfidf], [user_tfidf])
        user_recommendations.append((movie[0], sim))

        # print sim
    break

    # users[userid] = user_recommendations
    # exit()

    # print users
    # exit()

kMostSimilar = sorted(user_recommendations, key=lambda tup: tup[1], reverse=True)[:30]
print kMostSimilar

# kMostSimilar = sorted(users[userid], key=lambda tup: tup[1], reverse=True)[:30]
# print kMostSimilar