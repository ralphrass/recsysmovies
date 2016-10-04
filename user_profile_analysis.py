import sqlite3
import random
import utils
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier

conn = sqlite3.connect('database.db')

LOW_LEVEL_FEATURES, DEEP_FEATURES, HYBRID_FEATURES = utils.extract_features()
features = DEEP_FEATURES

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
c = conn.cursor()
c.execute(sql, (user,))

all_movies = c.fetchall()

try:
    full_training_set = random.sample(all_movies, int(len(all_movies) * 0.8))

    elite_training_set = []
    for item in full_training_set:
        if item[1] >= 4:
            elite_training_set.append(item)

    full_test_set = [x for x in all_movies if x not in full_training_set]
    elite_test_set = []
    for item in full_test_set:
        if item[1] >= 4:
            elite_test_set.append(item)
except:
    print "Error"
    raise

userInstances, userValues = utils.getUserInstances(full_training_set, features)
train_values = [1 if x > 4 else 0 for x in userValues]
test_instances, test_values = utils.getUserInstances(full_test_set, features)
test_real_values = [1 if x > 4 else 0 for x in test_values]
# gnb = GaussianNB()
# model = gnb.fit(userInstances, train_values)
clf = svm.SVC(kernel='rbf', C=0.1)
clf.fit(userInstances, train_values)
y_pred = clf.predict(test_instances)
# print y_pred
print "SVM"
print("Number of mislabeled points out of a total %d points : %d, inaccuracy: %d"
      % (np.array(test_instances).shape[0],(test_real_values != y_pred).sum(),
         ((test_real_values != y_pred).sum()*100)/np.array(test_instances).shape[0])+"%" )


print "kNN"
neigh = KNeighborsClassifier(n_neighbors=20, weights='distance')
neigh.fit(userInstances, train_values)
y_pred = neigh.predict(test_instances)
print("Number of mislabeled points out of a total %d points : %d, inaccuracy: %d"
      % (np.array(test_instances).shape[0],(test_real_values != y_pred).sum(),
         ((test_real_values != y_pred).sum()*100)/np.array(test_instances).shape[0])+"%" )

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
