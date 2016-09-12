import constants
import recommender
import evaluation
import utils

def main():

    constants.NUM_USERS = 100 # constants.MAX_NUM_USERS
    constants.PREDICTION_LIST_SIZE = 50 #increase at each iteration
    constants.LIMIT_ITEMS_TO_PREDICT = 100 #constants.MAX_ITEMS_TO_PREDICT #list of all movies
    iterations = 10

    print "Starting Experiment... ", iterations, "iterations.", constants.NUM_USERS, "users.", "recommender list size equal to", constants.PREDICTION_LIST_SIZE, "." , constants.LIMIT_ITEMS_TO_PREDICT, "items to predict for"

    for i in range(iterations):

        print i, "iteration."

        Users = utils.selectRandomUsers()
        MoviesToPredict = utils.selectRandomMovies()

        constants.LIMIT_ITEMS_TO_PREDICT += 25

        RandomMAE = evaluation.evaluateRandomMAE(Users, MoviesToPredict, False)

        randomresult = str(RandomMAE)
        with open('REAL_RANDOM_MAE-100users-100items-10iterations-25Plus-List50.txt', 'a') as f:
            f.write("\nRandom MAE "+randomresult+"\n\n")
        print "Random MAE ", (RandomMAE)

    constants.conn.close()

if __name__ == '__main__':
    main()
