import sqlite3
import recommender
from utils import extract_features
from time import time
import cPickle as pickle
import opening_feat as of

LOW_LEVEL_FEATURES, DEEP_FEATURES_BOF, HYBRID_FEATURES_BOF = extract_features('bof_128.bin')

conn = sqlite3.connect('database.db')

start = time()

sql = "SELECT t.id " \
      "FROM trailers t " \
      "JOIN movielens_movie m on m.imdbidtt = t.imdbid " \
      "WHERE t.best_file = 1 " \
      "AND m.movielensid in (select distinct movielensid from movielens_rating) "
      # "LIMIT 100"

c = conn.cursor()
c.execute(sql)
all_movies = c.fetchall()

similarities = {}

mid = time()

print mid - start, "seconds"

count = 0

for movie in all_movies:
    subsims = {}
    for movie_j in all_movies:
        count += 1
        try:
            cos = float(recommender.cosine(movie, movie_j, HYBRID_FEATURES_BOF))
            subsims[movie_j[0]] = cos
        except KeyError:
            print movie, movie_j, "error"
            continue
    similarities[movie[0]] = subsims

print similarities[2]

mid = time()

print mid - start, "seconds"

with open('movie_cosine_similarities_hybrid.bin','wb') as fp:
    pickle.dump(similarities,fp, protocol=2)

similarities = of.load_features('movie_cosine_similarities_hybrid.bin')

print similarities[2]