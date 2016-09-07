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
    "both", #quanti + quali
    "triple" #both + features from trailers
]

def main():

    constants.NUM_USERS = 100 # constants.MAX_NUM_USERS
    constants.PREDICTION_LIST_SIZE = 100 #increase at each iteration
    constants.LIMIT_ITEMS_TO_PREDICT = 100 #constants.MAX_ITEMS_TO_PREDICT #list of all movies
    constants.LIMIT_ITEMS_TO_COMPARE = 100 # constants.MAX_ITEMS_TO_COMPARE #movies rated by each user
    recommender.RECOMMENDATION_STRATEGY = 'triple' #quanti, quali, both, triple(quanti, quali and features)
    iterations = 2
    outsideiterations = 2

    print "Starting Experiment... ", iterations, "iterations.", constants.NUM_USERS, "users.", "recommender list size equal to", constants.PREDICTION_LIST_SIZE, "." , constants.LIMIT_ITEMS_TO_PREDICT, "items to predict for.", constants.LIMIT_ITEMS_TO_COMPARE, "items of each user to compare with."

    #TODO Randomize each user, items to recommend and items to compare with. Run for 'n' iterations and collect average MAE
    #TODO matplotlib

    #rfile = open('results', 'a')

    for k in range(outsideiterations):

        AVG_MAE = {"quanti": {}, "quali": {}, "both": {}, "triple": {}}
        AVG_MAE["quanti"]["gower"] = 0
        AVG_MAE["quanti"]["cos-content"] = 0
        AVG_MAE["quanti"]["gower-features"] = 0
        AVG_MAE["quanti"]["cos-features"] = 0
        AVG_MAE["quali"]["gower"] = 0
        AVG_MAE["quali"]["cos-content"] = 0
        AVG_MAE["quali"]["gower-features"] = 0
        AVG_MAE["quali"]["cos-features"] = 0
        AVG_MAE["both"]["gower"] = 0
        AVG_MAE["both"]["cos-content"] = 0
        AVG_MAE["both"]["gower-features"] = 0
        AVG_MAE["both"]["cos-features"] = 0
        AVG_MAE["triple"]["gower"] = 0
        AVG_MAE["triple"]["cos-content"] = 0
        AVG_MAE["triple"]["gower-features"] = 0
        AVG_MAE["triple"]["cos-features"] = 0
        AVG_RANDOM_MAE = 0
        AVG_RECALL = {"quanti": {}, "quali": {}, "both": {}, "triple": {}}
        AVG_RECALL["quanti"]["gower"] = 0
        AVG_RECALL["quanti"]["cos-content"] = 0
        AVG_RECALL["quanti"]["gower-features"] = 0
        AVG_RECALL["quanti"]["cos-features"] = 0
        AVG_RECALL["quali"]["gower"] = 0
        AVG_RECALL["quali"]["cos-content"] = 0
        AVG_RECALL["quali"]["gower-features"] = 0
        AVG_RECALL["quali"]["cos-features"] = 0
        AVG_RECALL["both"]["gower"] = 0
        AVG_RECALL["both"]["cos-content"] = 0
        AVG_RECALL["both"]["gower-features"] = 0
        AVG_RECALL["both"]["cos-features"] = 0
        AVG_RECALL["triple"]["gower"] = 0
        AVG_RECALL["triple"]["cos-content"] = 0
        AVG_RECALL["triple"]["gower-features"] = 0
        AVG_RECALL["triple"]["cos-features"] = 0

        print "Outside iteration", k

        for i in range(iterations):

            print i, "iteration."
            recommender.AVERAGE_RANDOM_MAE = 0 #need to compute for every iteration

            for strategy in STRATEGIES:

                recommender.RECOMMENDATION_STRATEGY = strategy
                # print "\nStrategy", recommender.RECOMMENDATION_STRATEGY
                # Vary the number of items used for similarity computation to measure MAE from 25 to 500 (+25 at each iteration)
                for m in MEASURES:

                    #print "Computing measure", m
                    recommender.SIMILARITY_MEASURE = m
                    SumMAE, CountUsers, SumRandomMAE, UsersPredictions, UsersRandomPredictions = recommender.main()
                    MAE, RandomMAE = evaluation.evaluateAverageMAE(SumMAE, CountUsers, SumRandomMAE)
                    Precision, Recall, F1 = evaluation.evaluatePrecisionRecallF1(UsersPredictions, CountUsers)
                    if recommender.AVERAGE_RANDOM_MAE == 0:
                        recommender.AVERAGE_RANDOM_MAE = RandomMAE #used to ensure that it will be computed only once
                        AVG_RANDOM_MAE += RandomMAE
                    AVG_MAE[strategy][m] += MAE
                    AVG_RECALL[strategy][m] += Recall

        constants.NUM_USERS += 10

        with open('file.txt', 'a') as resfile:
            for measure in AVG_MAE:
                for mae in AVG_MAE[measure]:
                    resmae = str(AVG_MAE[measure][mae] / iterations)
                    resrecall = str(AVG_RECALL[measure][mae])
                    res = str("Measure "+measure+" Strategy "+mae+" MAE "+resmae+" Recall "+resrecall)
                    resfile.write(res)
                    print res
                    #print "Measure", measure, "Strategy",mae, " MAE ", (AVG_MAE[measure][mae] / iterations), "Recall ", AVG_RECALL[measure][mae]

        randomresult = str(AVG_RANDOM_MAE / iterations)
        with open('file.txt', 'a') as f:
            f.write("Random MAE "+randomresult+"\n\n")
        print "Random MAE ", (AVG_RANDOM_MAE / iterations)

    constants.conn.close()
    #rfile.close()

if __name__ == '__main__':
    main()
