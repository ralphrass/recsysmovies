import constants
import recommender
import evaluation

MEASURES = [
    "gower",
    "cos-content",
    "gower-features",
    "cos-features"

    # "cos-collaborative",
    # "adjusted-cosine"
]

STRATEGIES = [
    "quanti", #quantitative features (Year, MovieLens Rating, IMDB Rating, Tomato Rating)
    "quali", #Actors, Director, Writer
    #"both", #quanti + quali
    "triple" #both + features from trailers
]

def main():

    constants.NUM_USERS = 10 # constants.MAX_NUM_USERS
    constants.PREDICTION_LIST_SIZE = 10 #increase at each iteration
    constants.LIMIT_ITEMS_TO_PREDICT = 20 #constants.MAX_ITEMS_TO_PREDICT #list of all movies
    constants.LIMIT_ITEMS_TO_COMPARE = 20 # constants.MAX_ITEMS_TO_COMPARE #movies rated by each user
    recommender.RECOMMENDATION_STRATEGY = 'triple' #quanti, quali, both, triple(quanti, quali and features)

    print "Starting Experiment... ", constants.NUM_USERS, "users.", "recommender list size equal to", constants.PREDICTION_LIST_SIZE, "." , constants.LIMIT_ITEMS_TO_PREDICT, "items to predict for.", constants.LIMIT_ITEMS_TO_COMPARE, "items of each user to compare with."

    #TODO Ensure that gower-features and cos-features is computed once for each strategy (except triple)
    #TODO matplotlib

    for strategy in STRATEGIES:

        recommender.RECOMMENDATION_STRATEGY = strategy
        print "\nStrategy", recommender.RECOMMENDATION_STRATEGY

        # Vary the number of items used for similarity computation to measure MAE from 25 to 500 (+25 at each iteration)

        for m in MEASURES:

            if (strategy == 'quali') and (m != 'gower'):
                continue

            print "Computing measure", m
            recommender.SIMILARITY_MEASURE = m
            SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions = recommender.main()
            MAE, RandomMAE = evaluation.evaluateAverageMAE(SumMAE, CountUsers, SumRandomMAE)
            if recommender.AVERAGE_RANDOM_MAE == 0:
                recommender.AVERAGE_RANDOM_MAE = RandomMAE
            print "MAE ", MAE

    print "Random MAE ", recommender.AVERAGE_RANDOM_MAE
    constants.conn.close()

if __name__ == '__main__':
    main()
