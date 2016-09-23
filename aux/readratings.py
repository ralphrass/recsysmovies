import sqlite3
import csv
#import sys

conn = sqlite3.connect('database.db')
c = conn.cursor()
movies = 1
count=0
ratings = []

with open('ratings.csv') as csvfile: #userId,movieId,rating,timestamp
    reader = csv.DictReader(csvfile)
    for rating in reader:
        print "searching ratings for movie ", movies
        movies += 1
        print rating['movieId']
        c.execute('SELECT movielensID FROM movielens_movie WHERE movielensID = ?', (rating['movieId'],))
        if (not c.fetchone()):
            print "rating ", movies, " nao encontrado para o filme ", rating['movieId'], "."
        else:
            ratings.append((rating['movieId'], rating['userId'], rating['rating']))
            count += 1
            print "appended ", count, " ratings."
            #sys.exit(0)
c.executemany('INSERT INTO movielens_rating(movielensID, userId, rating) VALUES (?,?,?)', ratings)
conn.commit()
conn.close()
