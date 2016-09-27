import sqlite3
import numpy as np
np.set_printoptions(threshold=np.inf)
import utils

# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, utils.adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", utils.convert_array)
conn = sqlite3.connect('../database.db', detect_types=sqlite3.PARSE_DECLTYPES)

# TOTAL_USERS = 5363
TOTAL_USERS = float(4897)

sql = "SELECT DISTINCT t.userid FROM movielens_tag t JOIN movielens_training_dataset mtd ON mtd.movielensid = t.movielensid "
sql_all_tags = "SELECT tag FROM movielens_all_tags"
# sql_tags = "SELECT tag, COUNT(*) FROM movielens_tag WHERE userid = ? GROUP BY tag"s

sql_tags = "SELECT t.tag, COUNT(*) " \
           "FROM movielens_tag t " \
           "JOIN movielens_rating r ON r.userid = t.userid AND r.movielensid = t.movielensid " \
           "JOIN movielens_training_dataset mtd ON mtd.movielensid = r.movielensid " \
           "WHERE t.userid = ? AND r.rating > 3 " \
           "GROUP BY t.tag"

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

sqlI = "INSERT INTO movielens_user_tfidf_profile VALUES(?, ?)"
profiles = []

for user in users:

    c = conn.cursor()
    c.execute(sql_tags, (user[0],))
    tags = c.fetchall()

    user_profile_tfidf = np.zeros(len(all_tags), dtype=np.float)

    for tag in tags:
        tf = float(tag[1])
        idf = float(np.log(TOTAL_USERS / getUsersByTag(conn, tag[0])))
        tfidf = float(tf * idf)
        user_profile_tfidf[all_tags.index(str(tag[0]))] = tfidf

    c = conn.cursor()
    c.execute(sqlI, (user[0], user_profile_tfidf,))
    break
    # profiles.append((user[0], user_profile_tfidf))

conn.commit()
conn.close()