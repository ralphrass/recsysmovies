import sqlite3
import numpy as np

conn = sqlite3.connect('../database.db')

# sql = "SELECT DISTINCT m.movielensid, m.userid, m.rating FROM movielens_rating m "
sql = "SELECT m.movielensid, m.userid, m.rating " \
      "FROM movielens_rating m " \
      "EXCEPT " \
      "SELECT movielensid, userid, rating " \
      "FROM movielens_rating_test t "
c = conn.cursor()
c.execute(sql)
# movies = [x[0] for x in c.fetchall()]
movies = c.fetchall()

# test_dataset = np.random.choice(movies, len(movies)*0.2, replace=False)
# np.random.shuffle(movies)
# test_dataset = movies[:int(len(movies)*0.02)] # 2% of the ratings will be the test set

sqlI = "INSERT INTO movielens_rating_training VALUES(?, ?, ?)"

for movie in movies:
    c = conn.cursor()
    c.execute(sqlI, movie)

conn.commit()
conn.close()