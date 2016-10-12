import random
import utils


def recommend(user_profiles, N):

    sum_recall, sum_precision = 0, 0

    for user, profile in user_profiles.iteritems():
        # print "Training User", user[0], " model..."
        if len(profile['elite_predictions']) == 0:
            continue

        hits = 0

        # For each item rated high by the user
        for elite_movie in profile['elite_predictions']['random']:
            if elite_movie[2] > predictions[2]:
                index = predictions.index(prediction)
                return int(index < n)

            # print sorted(predictions, key=lambda tup: tup[2], reverse=True)
            predictions_ids = [x[0] for x in sorted(current_predictions, key=lambda tup: tup[2], reverse=True)]
            eliteIndex = predictions_ids.index(elite_movie[2])
            # print eliteMovie, eliteIndex
            if eliteIndex < N:
                hits += 1

        recall = hits / float(len(datasets['elite_test']))
        sum_recall += recall
        if N > 0:
            sum_precision += (recall / float(N))

    size = len(user_profiles)
    avgRecall = utils.evaluateAverage(sum_recall, size)
    avgPrecision = utils.evaluateAverage(sum_precision, size)

    return avgPrecision, avgRecall
