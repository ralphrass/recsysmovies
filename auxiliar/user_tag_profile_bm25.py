import sqlite3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfTransformer
np.set_printoptions(threshold=np.inf)
import random
from sklearn.feature_extraction import DictVectorizer
import cPickle as pickle

conn = sqlite3.connect('../database.db')
_total_users = 0

def get_tag_counts(user):

    global conn

    sql_tag = "SELECT t.tag, COUNT(*) FROM movielens_tag t " \
              "JOIN movielens_rating r ON r.movielensid = t.movielensid AND r.userid = t.userid " \
              "WHERE t.userid = ? " \
              "AND r.rating > 4 " \
              "GROUP BY t.tag "
    c = conn.cursor()
    c.execute(sql_tag, (user,))

    return c.fetchall()


def get_users_by_tag(tag):

    sql = "SELECT COUNT(*) FROM movielens_tag WHERE tag = ?"
    c = conn.cursor()
    c.execute(sql, (tag,))

    return c.fetchall()

def comput_user_okapi(user):

    k1 = 2
    b = 0.75

    user_profile = []
    counts = get_tag_counts(user)
    avg_count = sum([x[1] for x in counts]) / len(counts)

    for count in counts:
        user_iuf = np.log(_total_users / get_users_by_tag(count[0]))
        res =( (count[1] * (k1 + 1)) / (count[1] + k1 * (1-b + b * (len(counts) / avg_count))) ) * user_iuf
        user_profile.append(res)


# read tags and tag counts for each user
# sql_user = "SELECT DISTINCT r.userid FROM movielens_user r "
#             # "JOIN movielens_tag t ON t.movielensid = r.movielensID AND t.userid = r.userid "
# c = conn.cursor()
# c.execute(sql_user)
# users = [u[0] for u in c.fetchall()]
#
# sql_movies = "SELECT DISTINCT m.movielensid FROM movielens_movie m "
#              # "JOIN movielens_tag t ON t.movielensid = m.movielensid"
# c = conn.cursor()
# c.execute(sql_movies)
# movies = [m[0] for m in c.fetchall()]
#
# sql_tag = "SELECT t.tag, COUNT(*) FROM movielens_tag t " \
#            "JOIN movielens_rating r ON r.movielensid = t.movielensid AND r.userid = t.userid " \
#            "WHERE t.userid = ? " \
#            "AND r.rating > 4 " \
#            "GROUP BY t.tag "
# sql_movie_tag = sql_tag.replace('t.userid = ?', 't.movielensid = ?')
#
# all_users_profiles = []
#
# for user in users:
#     c = conn.cursor()
#     c.execute(sql_tag, (user,))
#     all_t = c.fetchall()
#     training_set = random.sample(all_t, int(len(all_t) * 0.8))
#     all_users_profiles.append(dict(training_set))
#
# unique_tag_set = set( val for dic in all_users_profiles for val in list(dic.keys()))
# # print len(unique_tag_set)
# # print unique_tag_set
# # exit()
# all_movies_profiles = []
#
# for movie in movies:
#     c = conn.cursor()
#     c.execute(sql_movie_tag, (movie,))
#     all_t = c.fetchall()
#
#     # guarantee that movies and users have the same vector size
#     filtered_tags = []
#     for tag in all_t:
#         if tag[0] in unique_tag_set:
#             filtered_tags.append(tag)
#
#     all_movies_profiles.append(dict(filtered_tags))

# unique_tag_set = set( val for dic in all_movies_profiles for val in list(dic.keys()))
# print len(unique_tag_set)
# print unique_tag_set
# exit()

# v = DictVectorizer(sparse=False)
# transformer = TfidfTransformer(smooth_idf=False)
#
# user_profiles = v.fit_transform(all_users_profiles)
# movies_profiles = v.fit_transform(all_movies_profiles)
# tfidf_users = transformer.fit_transform(user_profiles)
# tfidf_movies = transformer.fit_transform(movies_profiles)
#
# users_tfidf_dict = dict(zip(users, tfidf_users.toarray()))
# movies_tfidf_dict = dict(zip(movies, tfidf_movies.toarray()))
#
# with open('users_tfidf_profile.bin','wb') as fp:
#     pickle.dump(users_tfidf_dict,fp, protocol=2)
#
# with open('movies_tfidf_profile.bin','wb') as fp:
#     pickle.dump(movies_tfidf_dict,fp, protocol=2)

# print tfidf_movies.toarray()

# print tfidf.toarray()
# print X
# print all_users_profiles[:1]

    # print user_tags_dict
    # break

# sql_user = "SELECT t.tag, COUNT(*) FROM movielens_tag t "


# organize user's feature vectors as dictionaries

# aggreagate dictionaries in a list

# apply DictVectorizer transformation