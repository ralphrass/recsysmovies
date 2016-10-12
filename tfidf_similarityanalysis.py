from scipy.spatial.distance import cosine
from opening_feat import load_features
import sqlite3
import scipy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.stats import pearsonr
from scipy.spatial.distance import minkowski
from sklearn import preprocessing
import itertools as it
import opening_feat as of

user_features = of.load_features('users_tfidf_profile.bin')
movie_features = of.load_features('movies_tfidf_profile.bin')

conn = sqlite3.connect('database.db')

# trailerid = 2216 # Jurassic World
movielensid = 4993 # the lord of the rings
# movielensid = 2571 # Matrix
# trailerid = 5632 # ToyStory
# trailerid = 2
# trailerid = 3341
# movie = low_level_features[trailerid]
# movie = features[trailerid]

# movie = features[3412] # Se7en
# movie = features[5612] #Django Unchained
# movie = low_level_features[4484] # Matrix
movie = movie_features[movielensid]

# print lordoftherings
similarities_cosine = []
# similarities_pearson = []
similarities_euclidean = []
# similarities_minkowski = []
# similarities_ratings = []

# similarities_cosine_hibryd = []
# similarities_pearson_hibryd = []
# similarities_euclidean_hibryd = []
# similarities_minkowski_hibryd = []

# similarities = {"cosine": [], "pearson": [], "euclidean": []}
sort_func = lambda x: sorted(x, key=lambda tup: tup[1], reverse=True)

for key, movief in movie_features.iteritems():

    # x = np.array(movief)
    # y = np.array(movie)

    # simr = pearsonr(x, y)
    # simmink = minkowski(x, y, 3)

    # simr_hybrid = pearsonr(vI, vJ)
    # simmink_hybrid = minkowski(vI, vJ, 5)

    # x = x.reshape(1, -1)
    # y = y.reshape(1, -1)

    # vI = vI.reshape(1, -1)
    # vJ = vJ.reshape(1, -1)

    sim = cosine_similarity([movie], [movief])
    # sime = euclidean_distances(x, y)

    # sim_hybrid = cosine_similarity(vI, vJ)
    # sime_hybrid = euclidean_distances(vI, vJ)
    sql = "SELECT title FROM movielens_movie WHERE movielensid = ?"
    c = conn.cursor()
    c.execute(sql, (key,))
    title = c.fetchall()

    similarities_cosine.append((title[0], sim))
    # similarities_pearson.append((title[0], simr))
    # similarities_euclidean.append((title[0], sime))
    # similarities_minkowski.append((title[0], simmink))


    # similarities_cosine_hibryd.append((title[0], sim_hybrid))
    # similarities_pearson_hibryd.append((title[0], simr_hybrid))
    # similarities_euclidean_hibryd.append((title[0], sime_hybrid))
    # similarities_minkowski_hibryd.append((title[0], simmink_hybrid))

# print similarities
# similarities["cosine"] = sort_func(similarities_cosine)
# similarities["pearson"] = sort_func(similarities_pearson)
# similarities["euclidean"] = sort_func(similarities_euclidean)

topsims_cosine = sorted(similarities_cosine, key=lambda tup: tup[1], reverse=True)
# topsims_pearson = sorted(similarities_pearson, key=lambda tup: tup[1], reverse=True)
# topsims_euclidean = sorted(similarities_euclidean, key=lambda tup: tup[1], reverse=False)
# topsims_minkowski = sorted(similarities_minkowski, key=lambda tup: tup[1], reverse=False)
# topsims_ratings = sorted(similarities_ratings, key=lambda tup: tup[1], reverse=True)

# topsims_cosine_hybrid = sorted(similarities_cosine_hibryd, key=lambda tup: tup[1], reverse=True)
# topsims_pearson_hybrid = sorted(similarities_pearson_hibryd, key=lambda tup: tup[1], reverse=True)
# topsims_euclidean_hybrid = sorted(similarities_euclidean_hibryd, key=lambda tup: tup[1], reverse=False)
# topsims_minkowski_hybrid = sorted(similarities_minkowski_hibryd, key=lambda tup: tup[1], reverse=False)

# print "Cosine Ratings"
# print topsims_ratings[:50]

print "Cosine"
# print topsims_cosine
for key, value in enumerate(topsims_cosine):
    print key, value

# print "Euclidean"
# for key, value in enumerate(topsims_euclidean[:30]):
#     print key, value

# print "Cosine Hybrid"
# print topsims_cosine_hybrid[:50]
# print "Pearson"
# print topsims_pearson[:50]
# print "Pearson Hybrid"
# print topsims_pearson_hybrid[:50]
# print "Euclidean"
# print topsims_euclidean[:50]
# print "Euclidean Hybrid"
# print topsims_euclidean_hybrid[:50]
# print "Minkowski"
# print topsims_minkowski[:50]
# print "Minkowski Hybrid"
# print topsims_minkowski_hybrid[:50]

