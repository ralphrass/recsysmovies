import constants
import recommender
import evaluation

MEASURES = [
    "gower",
    "cos-content"
    # "cos-collaborative",
    # "adjusted-cosine"
]

def main():

    constants.NUM_USERS = 5
    constants.PREDICTION_LIST_SIZE = 50
    constants.LIMIT_ITEMS_TO_PREDICT = 100
    constants.LIMIT_ITEMS_TO_COMPARE = 25
    recommender.RECOMMENDATION_STRATEGY = 'quanti'

    # Vary the number of items used for similarity computation to measure MAE from 25 to 500 (+25 at each iteration)

    for m in MEASURES:
        # print m
        recommender.SIMILARITY_MEASURE = m
        SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions = recommender.main()
        MAE, RandomMAE = evaluation.evaluateAverageMAE(SumMAE, CountUsers, SumRandomMAE)
        print MAE, RandomMAE

    constants.conn.close()

if __name__ == '__main__':
    main()
