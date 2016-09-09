import constants
import recommender
import evaluation
import utils

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

    constants.NUM_USERS = 600 # constants.MAX_NUM_USERS
    constants.PREDICTION_LIST_SIZE = 100 #increase at each iteration
    constants.LIMIT_ITEMS_TO_PREDICT = 100 #constants.MAX_ITEMS_TO_PREDICT #list of all movies
    iterations = 10

    print "Starting Experiment... ", iterations, "iterations.", constants.NUM_USERS, "users.", "recommender list size equal to", constants.PREDICTION_LIST_SIZE, "." , constants.LIMIT_ITEMS_TO_PREDICT, "items to predict for"

    for i in range(iterations):

        print i, "iteration."

        Users = utils.selectRandomUsers()
        MoviesToPredict = utils.selectRandomMovies()

        AVG_MAE, AVG_RECALL = utils.initializeLists()

        for strategy in STRATEGIES:
            recommender.RECOMMENDATION_STRATEGY = strategy
            for m in MEASURES:
                if not (m in AVG_MAE[strategy]):
                    continue

                recommender.SIMILARITY_MEASURE = m
                SumMAE, SumRecall = recommender.main(Users, MoviesToPredict)

                AVG_MAE[strategy][m] = utils.evaluateAverage(SumMAE, constants.NUM_USERS)
                AVG_RECALL[strategy][m] = utils.evaluateAverage(SumRecall, constants.NUM_USERS)

        constants.LIMIT_ITEMS_TO_PREDICT += 50

        RandomMAE = evaluation.evaluateRandomMAE(Users)

        with open('imageNet-LSTM-128-600users-100items-10iterations-50Plus.txt', 'a') as resfile:
            for measure in AVG_MAE:
                for mae in AVG_MAE[measure]:
                    resmae, resrecall = str(AVG_MAE[measure][mae]), str(AVG_RECALL[measure][mae])
                    res = str("\nMeasure "+measure+" Strategy "+mae+" MAE "+resmae+" Recall "+resrecall)
                    resfile.write(res)
                    print res

        randomresult = str(RandomMAE)
        with open('imageNet-LSTM-128-600users-100items-10iterations-50Plus.txt', 'a') as f:
            f.write("\nRandom MAE "+randomresult+"\n\n")
        print "Random MAE ", (RandomMAE)

    constants.conn.close()

if __name__ == '__main__':
    main()
