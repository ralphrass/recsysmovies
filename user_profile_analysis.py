import sqlite3
import random
import utils
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import warnings
warnings.filterwarnings('error')

conn = sqlite3.connect('database.db')

LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES = utils.extract_features()
USER_TFIDF_FEATURES, MOVIE_TFIDF_FEATURES = utils.extract_tfidf_features()
features = DEEP_FEATURES.copy()

user = 96
user = 156
# user = 8405

# read user trailers
sql = "SELECT t.id, r.rating, m.movielensid, m.title " \
      "FROM trailers t " \
      "JOIN movielens_movie m ON m.imdbidtt = t.imdbid " \
      "JOIN movielens_rating r ON r.movielensid = m.movielensid " \
      "JOIN movies ms ON ms.imdbid = t.imdbid " \
      "WHERE t.best_file = 1 " \
      "AND r.userid = ? " \
      # "AND CAST(ms.imdbvotes AS NUMERIC) > 100 "

users = utils.selectRandomUsers(conn)
total_accuracy = 0
dataset_size = len(users)

for user in users:

    c = conn.cursor()
    c.execute(sql, (user[0],))

    all_movies = c.fetchall()

    try:
        full_training_set = random.sample(all_movies, int(len(all_movies) * 0.7))
        full_test_set = [x for x in all_movies if x not in full_training_set]
    except:
        print "Error"
        raise

    userInstances, userValues = utils.getUserInstances(full_training_set, features)

    # print userInstances

    train_values = [1 if x > 4 else 0 for x in userValues]
    test_instances, test_values = utils.getUserInstances(full_test_set, features)
    test_real_values = [1 if x > 4 else 0 for x in test_values]

    # print test_instances

    clf = svm.SVC(kernel='sigmoid', C=100, class_weight={0: 6})
    try:
        clf.fit(userInstances, train_values)
        y_pred = clf.predict(test_instances)
        # print y_pred
        # print np.array(test_real_values)
        # print (np.array(test_real_values) != y_pred)
        # print (np.array(test_real_values) != y_pred).sum()
        # print (test_real_values != y_pred).sum()
        accuracy = 100 - (((test_real_values != y_pred).sum() * 100) / np.array(test_instances).shape[0])
        total_accuracy += accuracy
    except:
        dataset_size -= 1
        continue

print "Average Accuracy for", dataset_size, "users: ", (total_accuracy/dataset_size), "%"
    # print y_pred
    # print "SVM"
    # print("Number of mislabeled points out of a total %d points : %d, inaccuracy: %d"
    #       % (np.array(test_instances).shape[0],(test_real_values != y_pred).sum(),
    #          ((test_real_values != y_pred).sum()*100)/np.array(test_instances).shape[0])+"%" )


# print "kNN"
# neigh = KNeighborsClassifier(n_neighbors=20, weights='distance')
# neigh.fit(userInstances, train_values)
# y_pred = neigh.predict(test_instances)
# print("Number of mislabeled points out of a total %d points : %d, inaccuracy: %d"
#       % (np.array(test_instances).shape[0],(test_real_values != y_pred).sum(),
#          ((test_real_values != y_pred).sum()*100)/np.array(test_instances).shape[0])+"%" )

# print "Gradient Boosting"
# clf = GradientBoostingClassifier(n_estimators=1000, learning_rate=0.1, max_depth=1, random_state=0).fit(userInstances, train_values)
# print clf.score(test_instances, test_real_values)

# clf = nn.MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
# clf.fit(userInstances, train_values)
# y_pred = clf.predict(test_instances)
# print "MLP"
# print("Number of mislabeled points out of a total %d points : %d, inaccuracy: %d"
#       % (np.array(test_instances).shape[0],(test_real_values != y_pred).sum(),
#          ((test_real_values != y_pred).sum()*100)/np.array(test_instances).shape[0])+"%" )
