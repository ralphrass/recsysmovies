import utils
import random
from sklearn.metrics.pairwise import cosine_similarity

_avg_ratings = 3.51611876907599
_std_deviation = 1.098732183


def cosine(movieI, movieJ, feature_vector):

    traileri = movieI[0]
    trailerj = movieJ[0]

    try:
        featuresI = feature_vector[traileri]
        featuresJ = feature_vector[trailerj]
    except KeyError:
        return 0

    return cosine_similarity([featuresI], [featuresJ])


def predict_user_rating(all_movies, movieI, feature_vector):

    numerator, denominator, prediction = float(0), float(0), float(0)
    all_similarities = [(movieJ, cosine(movieI, movieJ, feature_vector)) for movieJ in all_movies]

    for movieJ, sim in all_similarities:
        if sim > 0:
            numerator += (float(sim) * (float(movieJ[1])))
            denominator += abs(float(sim))

    if numerator != 0 and denominator != 0:
        prediction = float(numerator / float(denominator))

    return prediction


def get_predictions(random_movies, all_movies, feature_vector):

    predictions = []

    for random_movie in random_movies:
        # print "Prediction for ", random_movie
        try:
            prediction = predict_user_rating(all_movies, random_movie, feature_vector)
            predictions.append((random_movie[2], random_movie[3], prediction))
            # print prediction
        except KeyError:
            continue

    # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)
    return sorted(predictions, key=lambda tup: tup[2], reverse=True)


def get_random_predictions(movies):

    global _avg_ratings, _std_deviation

    predictions = [(movie[2], movie[3], random.gauss(_avg_ratings, _std_deviation)) for movie in movies]

    return sorted(predictions, key=lambda tup: tup[2], reverse=True)


def run(user_profiles, N, feature_vector, feature_vector_name):

    sum_recall, sum_precision = 0, 0

    for user, profile in user_profiles.iteritems():

        hits = 0

        for elite_movie in profile['elite_predictions'][feature_vector_name]:

            if feature_vector is list and elite_movie[0] not in feature_vector:
                continue

            hits += count_hit(profile['predictions'][feature_vector_name], elite_movie, N)

        if hits > 0:
            recall = hits / float(len(profile['elite_predictions'][feature_vector_name]))
            sum_recall += recall
            sum_precision += (recall / float(N))

    size = len(user_profiles)
    avgRecall = utils.evaluateAverage(sum_recall, size)
    avgPrecision = utils.evaluateAverage(sum_precision, size)

    return avgPrecision, avgRecall


def count_hit(predictions, elite_movie, n):

    for prediction in predictions:
        if elite_movie[2] > prediction[2]:
            index = predictions.index(prediction)
            return int(index < n)

    return 0


def build_user_profiles(conn, Users, feature_vectors):

    user_profiles, predictions = {}, {}

    for user in Users:

        userMoviesTraining, userMoviesTest, full_test_set, all_movies = utils.getUserTrainingTestMovies(conn, user[0])

        if len(userMoviesTest) == 0:
            continue

        random_movies = utils.getRandomMovieSet(conn, user[0])

        predictions_low_level = get_predictions(random_movies, all_movies, feature_vectors['low-level'])
        predictions_deep = get_predictions(random_movies, all_movies, feature_vectors['deep'])
        predictions_hybrid = get_predictions(random_movies, all_movies, feature_vectors['hybrid'])
        predictions_random = get_random_predictions(random_movies)

        elite_predictions_ll = get_predictions(userMoviesTest, all_movies, feature_vectors['low-level'])
        elite_predictions_deep = get_predictions(userMoviesTest, all_movies, feature_vectors['deep'])
        elite_predictions_hybrid = get_predictions(userMoviesTest, all_movies, feature_vectors['hybrid'])
        elite_predictions_random = get_random_predictions(userMoviesTest)

        user_profiles[user[0]] = {
                                  # 'datasets': {'all_movies': all_movies, 'train': userMoviesTraining,
                                  #              'elite_test': userMoviesTest,
                                  # 'test': full_test_set, 'random': random_movies},
                                  'userid': user[0],
                                  'predictions': {'low-level': predictions_low_level, 'deep': predictions_deep,
                                                  'hybrid': predictions_hybrid, 'random': predictions_random},
                                  'elite_predictions': {'low-level': elite_predictions_ll,
                                                        'deep': elite_predictions_deep,
                                                        'hybrid': elite_predictions_hybrid,
                                                        'random': elite_predictions_random}}
    return user_profiles
