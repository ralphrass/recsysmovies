# Simplicity is the final achievement. After one has played a vast quantity of notes and more notes, it is
# simplicity that emerges as the crowning reward of art. Frederic Chopin.

import utils
import random
from opening_feat import load_features
import numpy as np
import operator
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_absolute_error
from multiprocessing import Process, Manager

_avg_ratings = 3.51611876907599
_std_deviation = 1.098732183

user_features = load_features('users_tfidf_profile.bin')
movie_features = load_features('movies_tfidf_profile.bin')

# conn = sqlite3.connect('database.db')

def cosine(movieI, movieJ, feature_vector):

    traileri = movieI[0]
    trailerj = movieJ[0]

    try:
        featuresI = feature_vector[traileri]
        featuresJ = feature_vector[trailerj]
    except KeyError:
        return 0

    return cosine_similarity([featuresI], [featuresJ])


def tag_cosine_movie(movieid1, movieid2):

    try:
        movie1_tfidf = movie_features[movieid1]
        movie2_tfidf = movie_features[movieid2]
    except KeyError:
        return 0

    return cosine_similarity([movie1_tfidf], [movie2_tfidf])


def predict_user_rating(user_baseline, movieid, all_similarities, _ratings_by_movie, _global_average):

    global _avg_ratings

    # item_baseline = utils.getItemBaseline(user_baseline, movieid)
    item_baseline = utils.get_item_baseline(user_baseline, movieid, _ratings_by_movie, _global_average)
    user_item_baseline = (_avg_ratings + user_baseline + item_baseline)

    numerator = sum((rating - user_item_baseline) * sim if sim > 0 else 0 for rating, sim in all_similarities)
    denominator = reduce(operator.add, [abs(x[1]) for x in all_similarities])
    try:
        prediction = (numerator / denominator) + user_item_baseline
    except ZeroDivisionError:
        prediction = 0

    return prediction


def get_predictions(store_result, strategy, user_baseline, movies, all_movies, sim_matrix, _ratings_by_movie,
                    _global_average):

    predictions = [(movie[2], predict_user_rating(user_baseline, movie[2],
                                                  [(movieJ[1], sim_matrix[movieJ[0]][movie[0]])
                                                   for movieJ in all_movies], _ratings_by_movie, _global_average),
                    movie[0])
                   for movie in movies]

    # predictions = [predict_user_rating(user_baseline, movie[2],
    #                                    [(movieJ[1], sim_matrix[movieJ[0]][movie[0]]) for movieJ in all_movies],
    #                                    _ratings_by_movie, _global_average) for movie in movies]

    # try:
        # mae = mean_absolute_error([movie[1] for movie in movies], [movie[1] for movie in predictions])
        # mae = mean_absolute_error(movies, predictions)
    # except ValueError:
    #     mae = 0

    # predictions.sort(reverse=True)
    store_result[strategy] = sort_desc(predictions)
    # store_result[strategy+'-mae'] = mae


def get_tag_predictions(random_movies, all_movies):

    predictions = []

    for random_movie in random_movies:
        # print "Prediction for ", random_movie
        try:
            all_similarities = [(movieJ, tag_cosine_movie(movieJ[2], random_movie[2])) for movieJ in all_movies]
            prediction = predict_user_rating(all_similarities)
            predictions.append((random_movie[2], random_movie[3], prediction))
            # print prediction
        except KeyError:
            continue

    # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)
    return sorted(predictions, key=lambda tup: tup[2], reverse=True)


def get_random_predictions(movies):

    global _avg_ratings, _std_deviation

    # predictions = (np.random.uniform(low=0.5, high=5.0, size=len(movies))).tolist()
    random_movies = [(movie[2], random.uniform(0.5, 5), movie[0]) for movie in movies]
    random_movies = sort_desc(random_movies)

    # try:
    #     mae = mean_absolute_error(movies, predictions)
    # except ValueError:
    #     mae = 0

    return random_movies


def sort_desc(list_to_sort):

    list_to_sort.sort(key=operator.itemgetter(1), reverse=True)
    return list_to_sort


def evaluate(user_profiles, N, feature_vector_name):

    sum_recall, sum_precision, sum_false_positive_rate = 0, 0, 0
    sum_diversity = 0

    for user, profile in user_profiles.iteritems():

        relevant_set = profile['datasets']['relevant_movies']
        irrelevant_set = profile['datasets']['irrelevant_movies']

        full_prediction_set = profile['predictions'][feature_vector_name]
        # full_set.sort(reverse=True)
        topN = [x[0] for x in full_prediction_set[:N]]  # topN list composed by movies IDs

        # how many items of the relevant set are retrieved (top-N)?
        true_positives = float(sum([1 if movie[2] in topN else 0 for movie in relevant_set]))
        true_negatives = float(sum([1 if movie[2] not in topN else 0 for movie in irrelevant_set]))

        false_negatives = float(len(relevant_set) - true_positives)
        false_positives = float(len(irrelevant_set) - true_negatives)

        # print "Relevant Set", relevant_set
        # print "Size", len(relevant_set)
        # print "Irrelevant Set", irrelevant_set
        # print "Size", len(irrelevant_set)
        # print "Full Set", full_prediction_set
        # print len(full_prediction_set)
        # print "Feature Vector", feature_vector_name
        # print "True Positives", true_positives
        # print "True Negatives", true_negatives
        # print "False Negatives", false_negatives
        # print "False Positives", false_positives
        # print "Top-N", topN
        # exit()

        try:
            precision = true_positives / (true_positives + false_positives)
        except ZeroDivisionError:
            precision = 0

        recall = true_positives / (true_positives + false_negatives)

        sum_precision += precision
        sum_recall += recall

    size = len(user_profiles)
    return utils.evaluateAverage(sum_precision, size), utils.evaluateAverage(sum_recall, size)


def build_user_profile(users, feature_vectors, similarity_matrices, _ratings, _ratings_by_movie, _global_average):

    user_profiles, predictions = {}, {}
    manager = Manager()

    predictions = manager.dict()

    for user in users:

        user_baseline = utils.get_user_baseline(user[0], _ratings, _global_average)
        user_movies_test, all_movies, garbage_test_set = utils.getUserTrainingTestMovies(user[0])

        if len(user_movies_test) == 0:
            continue

        random_movies = utils.getRandomMovieSet(user[0])
        movies_set = user_movies_test + garbage_test_set + random_movies

        jobs = []

        for feature_vector in feature_vectors:
            if len(feature_vector[1]) == 5:  # LL
                sim_matrix = similarity_matrices[0]
                feature_vector_name = 'low-level'
            elif len(feature_vector[1]) == 128:  # Deep
                sim_matrix = similarity_matrices[1]
                feature_vector_name = 'deep'
            else:  # hybrid
                sim_matrix = similarity_matrices[2]
                feature_vector_name = 'hybrid'

            p = Process(target=get_predictions, args=(predictions, feature_vector_name, user_baseline, movies_set,
                                                      all_movies, sim_matrix, _ratings_by_movie, _global_average))
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()

        predictions_random = get_random_predictions(movies_set)

        user_profiles[user[0]] = {'datasets': {'relevant_movies': user_movies_test,
                                               'irrelevant_movies': garbage_test_set},
                                  'userid': user[0],
                                  'predictions': {'low-level': predictions['low-level'],
                                                  'deep': predictions['deep'],
                                                  'hybrid': predictions['hybrid'],
                                                  'random': predictions_random}}
    return user_profiles
