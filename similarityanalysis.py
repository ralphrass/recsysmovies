from scipy.spatial.distance import cosine
from opening_feat import load_features
import sqlite3
import scipy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

conn = sqlite3.connect('database.db')
# features = load_features('res_neurons_32_feat_1024_scenes_350.bin') #dictionary
features = load_features('res_neurons_places_gru_32_feat_1024_scenes_350.bin')
movie = features[5458] # the lord of the rings
# movie = features[3412] # Se7en

# print lordoftherings
similarities = []

for key, movief in features.iteritems():
    # sim = cosine(scipy.array(movief), scipy.array(seven))
    x = np.array(movief)
    y = np.array(movie)
    x = x.reshape(1, -1)
    y = y.reshape(1, -1)
    # print x, y
    # exit()
    sim = cosine_similarity(x, y)
    # print sim
    # exit()
    q = "SELECT m.title FROM movies m JOIN trailers t on t.imdbid = m.imdbid AND t.best_file = 1 WHERE t.id = ?"
    c = conn.cursor()
    c.execute(q, (key,))
    title = c.fetchone()
    if (type(title) is tuple):
        similarities.append((title[0], sim))
        # print title[0], sim
        # exit()
# print similarities
topsims = sorted(similarities, key=lambda tup: tup[1], reverse=True)
print topsims[:50]
