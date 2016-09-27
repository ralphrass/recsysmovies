from opening_feat import load_features
import numpy as np
from sklearn import preprocessing

low_level_features = load_features('low_level_dict.bin') # normalize
arr = np.array([x[1] for x in low_level_features.iteritems()])
normalized_ll_features = preprocessing.normalize(arr)[0]

