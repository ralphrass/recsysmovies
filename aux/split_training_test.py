import sqlite3
import numpy as np

conn = sqlite3.connect('../database.db')

sql = "SELECT DISTINCT m.movielensid FROM movielens_movie m JOIN movielens_tag t ON t.movielensid = m.movielensid "
c = conn.cursor()
c.execute(sql)
movies = [x[0] for x in c.fetchall()]

# test_dataset = np.random.choice(movies, len(movies)*0.2, replace=False)
np.random.shuffle(movies)
test_dataset = movies[:int(len(movies)*0.2)]

sqlI = "INSERT INTO movielens_test_dataset VALUES(?)"

for movie in test_dataset:
    c = conn.cursor()
    c.execute(sqlI, (movie,))

conn.commit()
conn.close()