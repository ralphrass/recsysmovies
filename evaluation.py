import utils


def evaluate(user_profiles, N, feature_vector_name, sim_matrix):

    sum_recall, sum_precision, sum_false_positive_rate, sum_diversity = 0, 0, 0, 0

    for user, profile in user_profiles.iteritems():

        relevant_set = profile['datasets']['relevant_movies']
        irrelevant_set = profile['datasets']['irrelevant_movies']
        full_prediction_set = profile['predictions'][feature_vector_name]

        topN = [x[0] for x in full_prediction_set[:N]]  # topN list composed by movies IDs
        rec_set = [x[2] for x in full_prediction_set[:N]]  # topN list composed by trailers IDs

        # how many items of the relevant set are retrieved (top-N)?
        true_positives = float(sum([1 if movie[2] in topN else 0 for movie in relevant_set]))
        true_negatives = float(sum([1 if movie[2] not in topN else 0 for movie in irrelevant_set]))

        false_negatives = float(len(relevant_set) - true_positives)
        false_positives = float(len(irrelevant_set) - true_negatives)

        if N > 1 and sim_matrix is not None:
            diversity = sum([sim_matrix[i][j] for i in rec_set for j in rec_set if i != j]) / 2
            sum_diversity += diversity

        try:
            precision = true_positives / (true_positives + false_positives)
        except ZeroDivisionError:
            precision = 0

        recall = true_positives / (true_positives + false_negatives)

        sum_precision += precision
        sum_recall += recall

    size = len(user_profiles)
    return utils.evaluateAverage(sum_precision, size), utils.evaluateAverage(sum_recall, size), \
           utils.evaluateAverage(sum_diversity, size)

