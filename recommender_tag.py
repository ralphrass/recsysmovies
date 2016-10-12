import utils
from sklearn.metrics.pairwise import cosine_similarity
import opening_feat as of

user_features = of.load_features('users_tfidf_profile.bin')
movie_features = of.load_features('movies_tfidf_profile.bin')


def cosine(user, movie):

    global user_features, movie_features

    try:
        user_profile = user_features[user]
        movie_profile = movie_features[movie]
    except KeyError:
        return 0

    return cosine_similarity([user_profile], [movie_profile])


def predict_user_rating(user_profile, movieI):

    all_movies = user_profile['datasets']['all_movies']
    numerator, denominator, prediction = float(0), float(0), float(0)

    all_similarities = [(movieJ, cosine(user_profile['userid'], movieJ[2])) for movieJ in all_movies]

    for movieJ, sim in all_similarities:
        if sim > 0:
            numerator += (float(sim) * (float(movieJ[1])))
            denominator += abs(float(sim))

    if numerator != 0 and denominator != 0:
        prediction = float(numerator / float(denominator))

    return prediction


def get_predictions(user_profile):

    predictions = []

    for random_movie in user_profile['datasets']['random']:
        # print "Prediction for ", random_movie
        try:
            prediction = predict_user_rating(user_profile, random_movie)
            predictions.append((random_movie[2], random_movie[3], prediction))
            # print prediction
        except KeyError:
            continue

    # print "Predictions", sorted(predictions, key=lambda tup: tup[2], reverse=True)
    return predictions


def get_prediction_elite(elite_movie, user_profile):

    prediction = predict_user_rating(user_profile, elite_movie)
    # print "Elite Prediction", (elite_movie[2], elite_movie[3], prediction)
    return elite_movie[2], elite_movie[3], prediction


def run(user_profiles, N):

    sum_recall, sum_precision = 0, 0

    for user, profile in user_profiles.iteritems():

        hits = 0

        # get predictions for each feature vector ?
        predictions = get_predictions(profile)

        for elite_movie in profile['datasets']['elite_test']:

            # Predict to the user movie and to random movies that the user did not rated
            # print predictions
            elite_prediction = get_prediction_elite(elite_movie, profile)
            all_predictions = predictions[:]
            all_predictions.append(elite_prediction)

            # print "Elite Movie", elite_movie, elite_prediction

            hits += count_hit(all_predictions, elite_movie, N)

        if hits > 0:
            recall = hits / float(len(profile['datasets']['elite_test']))
            sum_recall += recall
            sum_precision += (recall / float(N))

    size = len(user_profiles)
    avgRecall = utils.evaluateAverage(sum_recall, size)
    avgPrecision = utils.evaluateAverage(sum_precision, size)

    return avgPrecision, avgRecall


def count_hit(predictions, elite_movie, n):

    predictions_ids = [x[0] for x in sorted(predictions, key=lambda tup: tup[2], reverse=True)]
    eliteIndex = predictions_ids.index(elite_movie[2])

    return int(eliteIndex < n)
