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

conn = sqlite3.connect('database.db')
# features = load_features('res_neurons_32_feat_1024_scenes_350.bin') #dictionary
# features = load_features('res_neurons_places_gru_32_feat_1024_scenes_350.bin')
features = load_features('resnet_152_lstm_128.dct')
low_level_features = load_features('low_level_dict.bin') # normalize

arr = np.array([x[1] for x in low_level_features.iteritems()])
normalized_ll_features = preprocessing.normalize(arr)

print low_level_features[99]
exit()
# import itertools as it
# print list(it.izip(low_level_features.keys(), normalized_ll_features))
low_level_features = {k: v for k, v in it.izip(low_level_features.keys(), normalized_ll_features)}

# print low_level_features[1]
# print normalized_ll_features[1]
# exit()

# print low_level_features.items()[1]
#
# print low_level_features[1]
# arr = np.array([x[1] for x in low_level_features.iteritems()])
# print arr[0]
# print preprocessing.normalize(arr)[0]
# exit()
# trailerid = 5458 # the lord of the rings
trailerid = 5632 # ToyStory
# trailerid = 2
movie = low_level_features[trailerid]

# movie = features[3412] # Se7en
# movie = features[5612] #Django Unchained
# movie = features[4484] # Matrix

# print lordoftherings
similarities_cosine = []
# similarities_pearson = []
# similarities_euclidean = []
# similarities_minkowski = []
# similarities_ratings = []

# similarities_cosine_hibryd = []
# similarities_pearson_hibryd = []
# similarities_euclidean_hibryd = []
# similarities_minkowski_hibryd = []

# similarities = {"cosine": [], "pearson": [], "euclidean": []}
sort_func = lambda x: sorted(x, key=lambda tup: tup[1], reverse=True)

for key, movief in low_level_features.iteritems():

    # print np.array(movief)
    # print movie, type(movie)
    # print movief.reshape(-1, 1)
    # print movie.reshape(-1, 1)
    # exit()

    # sqlI = "SELECT r1.rating FROM movielens_rating r1, movielens_rating r2, movielens_movie m1, movielens_movie m2, trailers t1, trailers t2 " \
    #        "WHERE r1.userid = r2.userid " \
    #        "AND m1.movielensid = r1.movielensid " \
    #        "AND t1.imdbid = m1.imdbidtt " \
    #        "AND t1.id = ? " \
    #        "AND m2.movielensid = r2.movielensid " \
    #        "AND t2.imdbid = m2.imdbidtt " \
    #        "AND t2.id = ? " \
    #        "ORDER BY r1.userId"
    # c = conn.cursor()
    # c.execute(sqlI, (trailerid, key,))
    # ratingsI = np.array([x[0] for x in c.fetchall()])
    # sqlJ = sqlI.replace("r1.rating", "r2.rating")
    # c = conn.cursor()
    # c.execute(sqlJ, (trailerid, key,))
    # ratingsJ = np.array([x[0] for x in c.fetchall()])

    # vI = np.hstack((movie, ratingsI))
    # vJ = np.hstack((movief, ratingsJ))

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

    q = "SELECT m.title FROM movies m JOIN trailers t on t.imdbid = m.imdbid WHERE t.id = ? AND t.best_file = 1"
    c = conn.cursor()
    c.execute(q, (key,))
    title = c.fetchone()
    if (type(title) is tuple):

        # if (len(ratingsI) > 0 and len(ratingsJ) > 0):
            # simratings = cosine_similarity(ratingsI.reshape(1, -1), ratingsJ.reshape(1, -1))
            # similarities_ratings.append((title[0], simratings))

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
print topsims_cosine
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

