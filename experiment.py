import constants
import recommender
import evaluation
import utils

MEASURES = [
    # "gower",
    "cos-content",
    # "gower-features",
    "cos-features"
    # "cos-collaborative",
    # "adjusted-cosine"
]

STRATEGIES = [
    "quanti", #quantitative features (Year, MovieLens Rating, IMDB Rating, Tomato Rating)
    # "quali", #Actors, Director, Writer
    # "both", #quanti + quali
    "triple" #both + features from trailers
]

def main():

    constants.NUM_USERS = 100 # constants.MAX_NUM_USERS
    constants.PREDICTION_LIST_SIZE = 50 #increase at each iteration
    constants.LIMIT_ITEMS_TO_PREDICT = 100 #constants.MAX_ITEMS_TO_PREDICT #list of all movies
    iterations = 16

    print "Starting Experiment... ", iterations, "iterations.", constants.NUM_USERS, "users.", "recommender list size equal to", constants.PREDICTION_LIST_SIZE, "." , constants.LIMIT_ITEMS_TO_PREDICT, "items to predict for"

    for i in range(iterations):

        print i, "iteration."

        Users = utils.selectRandomUsers()
        MoviesToPredict = utils.selectRandomMovies()

        AVG_MAE, AVG_RECALL = utils.initializeLists()
        RandomMAE, UserAverageMAE = 0, 0

        for strategy in STRATEGIES:
            recommender.RECOMMENDATION_STRATEGY = strategy
            for m in MEASURES:
                if not (m in AVG_MAE[strategy]):
                    continue

                recommender.SIMILARITY_MEASURE = m
                # SumMAE, SumRecall = recommender.main(Users, MoviesToPredict)
                SumMAE = recommender.main(Users, MoviesToPredict)

                AVG_MAE[strategy][m] = utils.evaluateAverage(SumMAE, constants.NUM_USERS)
                # AVG_RECALL[strategy][m] = utils.evaluateAverage(SumRecall, constants.NUM_USERS)

        constants.LIMIT_ITEMS_TO_PREDICT += 25

        UserAverageMAE = evaluation.evaluateRandomMAE(Users, MoviesToPredict)
        RandomMAE = evaluation.evaluateRandomMAE(Users, MoviesToPredict, False)

        with open('12-09-2012-imageNet-LSTM-128-100users-100items-16iterations-25Plus-List50.txt', 'a') as resfile:
            for measure in AVG_MAE:
                for mae in AVG_MAE[measure]:
                    # resmae, resrecall = str(AVG_MAE[measure][mae]), str(AVG_RECALL[measure][mae])
                    resmae = str(AVG_MAE[measure][mae])
                    # res = str("\nMeasure "+measure+" Strategy "+mae+" MAE "+resmae+" Recall "+resrecall)
                    res = str("\nMeasure "+measure+" Strategy "+mae+" MAE "+resmae)
                    resfile.write(res)
                    print res

        useraverageresult = str(UserAverageMAE)
        with open('12-09-2012-imageNet-LSTM-128-100users-100items-16iterations-25Plus-List50.txt', 'a') as f:
            f.write("\User Average MAE "+useraverageresult+"\n\n")
        print "User Average MAE ", (UserAverageMAE)

        randomresult = str(RandomMAE)
        with open('12-09-2012-imageNet-LSTM-128-100users-100items-16iterations-25Plus-List50.txt', 'a') as f:
            f.write("\nRandom MAE "+randomresult+"\n\n")
        print "Random MAE ", (RandomMAE)

    constants.conn.close()

if __name__ == '__main__':
    main()
