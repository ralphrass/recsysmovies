import sqlite3
from math import sqrt
import time
start = time.time()

conn = sqlite3.connect('../database.db')

sql = "SELECT movielensid FROM movielens_movie WHERE movielensid not in (SELECT movie1 FROM movielens_similarity) " \
      "ORDER BY movielensid"
c = conn.cursor()
c.execute(sql+" LIMIT 1000")
movies = c.fetchall()

c = conn.cursor()
c.execute(sql)
allmovies = c.fetchall()

usedmovies = []

for mI in movies:

    similarities = []

    for mJ in allmovies:

        if mJ in usedmovies:
            continue

        movieI = mI[0]
        movieJ = mJ[0]

        SumNumerator, SumDenominator1, SumDenominator2 = 0, 0, 0

        query = "SELECT r.userId, u.avgrating FROM movielens_rating r JOIN movielens_user u ON u.userid = r.userId WHERE r.movielensId = ?"
        queryIntersect = query + " INTERSECT " + query
        c = conn.cursor()
        c.execute(queryIntersect, (movieI, movieJ,))
        users = c.fetchall()

        if not users:
            cosine = 0
        else:
            for user in users:
                query = "SELECT r.rating FROM movielens_rating r WHERE r.userId = ? AND r.movielensId = ?"
                c = conn.cursor()
                c.execute(query, (user[0], movieI,))
                ratingMovieI = c.fetchone()[0]

                c = conn.cursor()
                c.execute(query, (user[0], movieJ,))
                ratingMovieJ = c.fetchone()[0]

                # print "User ", user[0], " average ", userAverage, " Rating ", ratingMovieI, " Rating 2 ", ratingMovieJ

                SumNumerator += ((ratingMovieI - user[1]) * (ratingMovieJ - user[1]))
                SumDenominator1 += (ratingMovieI - user[1]) ** 2
                SumDenominator2 += (ratingMovieJ - user[1]) ** 2

        try:
            cosine = SumNumerator / (sqrt(SumDenominator1) * sqrt(SumDenominator2))
        except ZeroDivisionError:
            cosine = 0

        similarities.append((movieI, movieJ, cosine))
        # sqlI = "INSERT INTO movielens_similarity(movie1, movie2, adjustedcosine) VALUES(?, ?, ?)"
        # c = conn.cursor()
        # c.execute(sqlI, (movieI, movieJ, cosine,))
        # conn.commit()

        usedmovies.append(mI)

    sqlI = "INSERT INTO movielens_similarity(movie1, movie2, adjustedcosine) VALUES(?, ?, ?)"
    c = conn.cursor()
    c.executemany(sqlI, similarities)
    conn.commit()

end = time.time()
print(end - start)