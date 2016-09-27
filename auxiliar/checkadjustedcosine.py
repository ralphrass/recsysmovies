import sqlite3
from math import sqrt
import time

movieI = 170
movieJ = 714

conn = sqlite3.connect('../database.db')

SumNumerator, SumDenominator1, SumDenominator2 = 0, 0, 0

start = time.time()
# Select users that rated both movies
query = "SELECT r.userId, u.avgrating FROM movielens_rating r JOIN movielens_user u ON u.userid = r.userId WHERE r.movielensId = ?"
queryIntersect = query+" INTERSECT "+query
c = conn.cursor()
c.execute(queryIntersect, (movieI, movieJ,))
users = c.fetchall()

queryN = "SELECT SUM((r1.rating - u.avgrating) * (r2.rating - u.avgrating)) FROM movielens_user u " \
         "JOIN movielens_rating r1 ON r1.userid = u.userid AND r1.movielensid = "+str(movieI)+" " \
         "JOIN movielens_rating r2 ON r2.userid = u.userid AND r2.movielensid = "+str(movieJ)+" " \
         "WHERE u.userid IN (SELECT r.userId FROM movielens_rating r " \
         "JOIN movielens_user u ON u.userid = r.userId WHERE r.movielensId = "+str(movieI)+" " \
         "INTERSECT SELECT r.userId FROM movielens_rating r " \
         "JOIN movielens_user u ON u.userid = r.userId WHERE r.movielensId = "+str(movieJ)+")"
c = conn.cursor()
c.execute(queryN)
numerator = c.fetchone()[0]

queryD = "SELECT SUM((r1.rating - u.avgrating)*(r1.rating - u.avgrating)) FROM movielens_user u " \
           "JOIN movielens_rating r1 ON r1.userid = u.userid AND r1.movielensid = ? " \
           "WHERE u.userid IN (SELECT r.userId FROM movielens_rating r JOIN movielens_user u ON u.userid = r.userId " \
           "WHERE r.movielensId = ? INTERSECT SELECT r.userId FROM movielens_rating r " \
           "JOIN movielens_user u ON u.userid = r.userId WHERE r.movielensId = ?)"

c = conn.cursor()
c.execute(queryD, (movieI, movieI, movieJ,))
d1 = c.fetchone()[0]
c = conn.cursor()
c.execute(queryD, (movieJ, movieI, movieJ,))
d2 = c.fetchone()[0]

# print numerator / (sqrt(d1) * sqrt(d2))

end = time.time()
print(end - start)


start = time.time()
for user in users:
    query = "SELECT r.rating FROM movielens_rating r WHERE r.userId = ? AND r.movielensId = ?"
    c = conn.cursor()
    c.execute(query, (user[0], movieI,))
    ratingMovieI = c.fetchone()[0]

    c = conn.cursor()
    c.execute(query, (user[0], movieJ,))
    ratingMovieJ = c.fetchone()[0]

    # print "User ", user[0], " average ", userAverage, " Rating ", ratingMovieI, " Rating 2 ", ratingMovieJ

    SumNumerator += ( (ratingMovieI - user[1]) * (ratingMovieJ - user[1]) )
    SumDenominator1 += (ratingMovieI - user[1])**2
    SumDenominator2 += (ratingMovieJ - user[1])**2
# print SumNumerator
# print SumDenominator1, SumDenominator2
# print SumNumerator / (sqrt(SumDenominator1) * sqrt(SumDenominator2))
end = time.time()
print(end - start)