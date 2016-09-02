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
    recommender.RECOMMENDATION_STRATEGY = 'quanti'

    for m in MEASURES:
        print m
        recommender.SIMILARITY_MEASURE = m
        SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions = recommender.main()
        MAE, RandomMAE = evaluation.evaluateAverageMAE(SumMAE, CountUsers, SumRandomMAE)
        print MAE, RandomMAE

    constants.conn.close()

if __name__ == '__main__':
    main()
