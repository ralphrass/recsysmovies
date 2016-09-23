import sqlite3
import numpy as np

conn = sqlite3.connect('../database.db')

# TOTAL_USERS = 5363
TOTAL_USERS = 4897

sql = "SELECT DISTINCT t.userid FROM movielens_tag t JOIN movielens_training_dataset mtd ON mtd.movielensid = t.movielensid "
sql_all_tags = "SELECT tag FROM movielens_all_tags"
# sql_tags = "SELECT tag, COUNT(*) FROM movielens_tag WHERE userid = ? GROUP BY tag"

sql_tags = "SELECT t.tag, COUNT(*) " \
           "FROM movielens_tag t " \
           "JOIN movielens_rating r ON r.userid = t.userid AND r.movielensid = t.movielensid " \
           "JOIN movielens_training_dataset mtd ON mtd.movielensid = r.movielensid " \
           "WHERE t.userid = ? AND r.rating > 3 " \
           "GROUP BY t.tag"
print sql_tags
exit()

def getUsersByTag(conn, tag):
    sqluserbytag = "SELECT COUNT(DISTINCT userid) FROM movielens_tag WHERE tag LIKE ?"
    c = conn.cursor()
    c.execute(sqluserbytag, (tag,))
    totalTags = c.fetchone()[0]

    return totalTags


c = conn.cursor()
c.execute(sql)
users = c.fetchall()

c = conn.cursor()
c.execute(sql_all_tags)
all_tags = [str(x[0]) for x in c.fetchall()]
print all_tags

for user in users:

    c = conn.cursor()
    c.execute(sql_tags, (user[0],))
    tags = c.fetchall()

    user_profile_tfidf = np.zeros(len(all_tags))

    for tag in tags:
        tf = tag[1]
        idf = np.log(TOTAL_USERS / getUsersByTag(conn, tag[0]))
        tfidf = tf * idf
        user_profile_tfidf[all_tags.index(str(tag[0]))] = tfidf

    # print user_profile
    # exit()

    sqlI = "INSERT INTO movielens_user_tfidf_profile VALUES(?, ?)"
    c = conn.cursor()
    c.execute(sqlI, (user[0], np.array_str(user_profile_tfidf)))
    conn.commit()

conn.close()