import sqlite3
from decimal import Decimal

conn = sqlite3.connect("database.db")
c = conn.cursor()
c2 = conn.cursor()
c3 = conn.cursor()
c.execute("SELECT userId FROM movielens_user WHERE userId < 10000")

for user in c.fetchall():
    c2.execute("SELECT (SUM(rating)/COUNT(*)) FROM movielens_rating r WHERE r.userId = ?", (user))
    avg = Decimal(c2.fetchone()[0])
    print avg
    c3.execute("UPDATE movielens_user SET averagerating = ? WHERE userId = ?", (avg, user,))
    # c3.execute("UPDATE movielens_user SET avgrating = CAST(? AS REAL) WHERE userId = ?", (str(avg), user))

conn.commit()
conn.close()
