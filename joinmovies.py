import sqlite3
import csv
import string
import sys

conn = sqlite3.connect('database.db')
c = conn.cursor()
movielist = []
count=0

with open('links.csv') as csvfile: #movieId,imdbId,tmdbId
    #spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    reader = csv.DictReader(csvfile)
    for link in reader:
        #if (count == 2):
        #    break
        for movie in c.execute('SELECT imdbID FROM trailers t JOIN lmtd9_a l ON l.id = t.id'):
            imdbID = string.replace(movie[0], "tt", "")
            if (imdbID == link['imdbId']): # match
                movielensID = link['movieId']
                tmdbID = link['tmdbId']
                with open('movies.csv') as csvfile2: #movieId,title,genres
                    reader2 = csv.DictReader(csvfile2)
                    for movielensmovie in reader2:
                        if (movielensID == movielensmovie['movieId']): #match
                            movielist.append((movie[0], imdbID, movielensID, tmdbID, movielensmovie['title'].decode('utf-8'), movielensmovie['genres'].decode('utf-8')))
                            count += 1
                            print "appended ", count, " movies."
                            break
                            #if (count == 1):
                            #    print movielist
                                #sys.exit(0)

c.executemany('INSERT INTO movielens_movie(imdbIDtt, imdbID, movielensID, tmdbID, title, genres) VALUES (?,?,?,?,?,?)', movielist)
conn.commit()
conn.close()
