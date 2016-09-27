import sqlite3
import csv
#import sys

conn = sqlite3.connect('../database.db')
c = conn.cursor()
movies = 1
count=0
tags = []

with open('tags.csv') as csvfile: #userId,movieId,rating,timestamp
    reader = csv.DictReader(csvfile)
    for tag in reader:
        if movies % 1000 == 0:
            print movies, " movies readed"
        movies += 1
        c.execute('SELECT movielensID FROM movielens_movie WHERE movielensID = ?', (tag['movieId'],))
        if (not c.fetchone()):
            pass
            # print "tag ", movies, " nao encontrado para o filme ", tag['movieId'], "."
        else:
            tags.append((tag['movieId'], tag['userId'], buffer(tag['tag'])))
            count += 1
            if count % 1000 == 0:
                c.executemany('INSERT INTO movielens_tag(movielensID, userId, tag) VALUES (?,?,?)', tags)
                conn.commit()
                print "appended ", count, " tags."
                tags = []
            #sys.exit(0)
conn.close()
