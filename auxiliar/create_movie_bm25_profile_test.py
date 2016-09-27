import sqlite3
import numpy as np
np.set_printoptions(threshold=np.inf)
import utils
import operator

# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, utils.adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", utils.convert_array)
conn = sqlite3.connect('../database.db', detect_types=sqlite3.PARSE_DECLTYPES)

sql = "SELECT DISTINCT t.movielensid FROM movielens_tag t JOIN movielens_test_dataset mtd ON mtd.movielensid = t.movielensid"
# sql_tags = "SELECT tag, COUNT(*) FROM movielens_tag WHERE movielensid = ? GROUP BY tag"
sql_all_tags = "SELECT tag FROM movielens_all_tags"
sql_tags = "SELECT tag, COUNT(*) FROM movielens_tag t " \
           "JOIN movielens_rating r ON r.userid = t.userid AND r.movielensid = t.movielensid " \
           "JOIN movielens_test_dataset mtd ON mtd.movielensid = r.movielensid " \
           "WHERE t.movielensid = ? AND r.rating > 3 " \
           "GROUP BY tag"


# TOTAL_MOVIES = 580
TOTAL_MOVIES = float(2903)
TOTAL_TAGS = float(17508)

k1 = 0.75
b = float(2)
avg_tags = TOTAL_TAGS / TOTAL_MOVIES # pre-computed

def getUsersByTag(conn, tag):
    sqluserbytag = "SELECT COUNT(DISTINCT movielensid) FROM movielens_tag WHERE tag LIKE ?"
    c = conn.cursor()
    c.execute(sqluserbytag, (tag,))
    totalTags = c.fetchone()[0]

    return totalTags

c = conn.cursor()
c.execute(sql)
movies = c.fetchall()

c = conn.cursor()
c.execute(sql_all_tags)
all_tags = [str(x[0]) for x in c.fetchall()]
print all_tags

sqlI = "INSERT INTO movielens_movie_bm25_profile VALUES(?, ?)"

for movie in movies:

    c = conn.cursor()
    c.execute(sql_tags, (movie[0],))
    tags = c.fetchall()

    counts = [x[1] for x in tags]

    if len(counts) == 0:
        continue

    total_tags = reduce(operator.add, counts)

    movie_profile = np.zeros(len(all_tags), dtype=np.float)

    for tag in tags:
        tf = float(tag[1])
        idf = float(np.log(TOTAL_MOVIES / getUsersByTag(conn, tag[0])))
        bm25 = ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (total_tags / avg_tags)))) * idf
        # tfidf = float(tf * idf)
        movie_profile[all_tags.index(str(tag[0]))] = bm25

    # print np.array_str(movie_profile)
    # exit()

    c = conn.cursor()
    c.execute(sqlI, (movie[0], movie_profile,))

conn.commit()
conn.close()