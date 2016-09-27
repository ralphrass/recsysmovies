import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# for user in c.execute('SELECT userID from movielens_user WHERE avgrating IS NULL LIMIT 100'):
#     q = "SELECT SUM(r.rating)/COUNT(*) FROM movielens_rating r WHERE r.userId = ?"
#     c = conn.cursor()
#     c.execute(q, (user[0],))
#     userAverage = c.fetchone()
#
#     q = "UPDATE movielens_user SET avgrating = ? WHERE userId = ?"
#     c = conn.cursor()
#     c.execute(q, (userAverage[0],user[0],))
#     conn.commit()
#
# conn.close()

for i in range(2200):
    q = "UPDATE movielens_user SET avgrating = (SELECT SUM(r.rating)/COUNT(*) FROM movielens_rating r WHERE r.userId = movielens_user.userId) WHERE avgrating IS NULL LIMIT 50"
    c = conn.cursor()
    c.execute(q)
    conn.commit()

conn.close()
