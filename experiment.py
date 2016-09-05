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
    #"quali", #Actors, Director, Writer
    #"both", #quanti + quali
    "triple" #both + features from trailers
]

def main():

    constants.NUM_USERS = 100 # constants.MAX_NUM_USERS
    constants.PREDICTION_LIST_SIZE = 10 #increase at each iteration
    constants.LIMIT_ITEMS_TO_PREDICT = 10 #constants.MAX_ITEMS_TO_PREDICT #list of all movies
    constants.LIMIT_ITEMS_TO_COMPARE = 10 # constants.MAX_ITEMS_TO_COMPARE #movies rated by each user
    recommender.RECOMMENDATION_STRATEGY = 'triple' #quanti, quali, both, triple(quanti, quali and features)
    iterations = 1

    print "Starting Experiment... ", constants.NUM_USERS, "users.", "recommender list size equal to", constants.PREDICTION_LIST_SIZE, "." , constants.LIMIT_ITEMS_TO_PREDICT, "items to predict for.", constants.LIMIT_ITEMS_TO_COMPARE, "items of each user to compare with."

    #TODO Randomize each user, items to recommend and items to compare with. Run for 'n' iterations and collect average MAE
    #TODO matplotlib

    AVG_MAE = {"quanti": {}, "triple": {}}

    AVG_MAE["quanti"]["gower"] = 0
    AVG_MAE["quanti"]["cos-content"] = 0
    AVG_MAE["quanti"]["gower-features"] = 0
    AVG_MAE["quanti"]["cos-features"] = 0
    AVG_MAE["triple"]["gower"] = 0
    AVG_MAE["triple"]["cos-content"] = 0
    # AVG_MAE["triple"]["gower-features"] = 0
    # AVG_MAE["triple"]["cos-features"] = 0
    AVG_RANDOM_MAE = 0

    for i in range(iterations):

        print "\n",i, "iteration."
        recommender.AVERAGE_RANDOM_MAE = 0 #need to compute for every iteration

        for strategy in STRATEGIES:

            recommender.RECOMMENDATION_STRATEGY = strategy
            print "\nStrategy", recommender.RECOMMENDATION_STRATEGY

            # Vary the number of items used for similarity computation to measure MAE from 25 to 500 (+25 at each iteration)

            for m in MEASURES:

                if (strategy == 'quali') and (m != 'gower'):
                    continue

                if (strategy == 'triple') and (m != 'gower' or m != 'cos-content'):
                    continue

                print "Computing measure", m
                recommender.SIMILARITY_MEASURE = m
                SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions = recommender.main()
                MAE, RandomMAE = evaluation.evaluateAverageMAE(SumMAE, CountUsers, SumRandomMAE)
                if recommender.AVERAGE_RANDOM_MAE == 0:
                    recommender.AVERAGE_RANDOM_MAE = RandomMAE #used to ensure that it will be computed only once
                    AVG_RANDOM_MAE += RandomMAE
                    # print RandomMAE
                # print "MAE ", MAE
                AVG_MAE[strategy][m] += MAE

    for measure in AVG_MAE:
        for mae in AVG_MAE[measure]:
            print "Measure", measure, "Strategy",mae, " MAE ", (AVG_MAE[measure][mae] / iterations)

    print "Random MAE ", (AVG_RANDOM_MAE / iterations)
    constants.conn.close()

if __name__ == '__main__':
    main()
