import twitter as t
import time
import sqlite3

conn = sqlite3.connect('taki.db')
conn.create_function('REGEXP', 2, lambda x, y: 1 if re.search(x,y) else 0)
cursor = conn.cursor()

cursor.execute(
    '''SELECT * FROM "main.Songs"
    WHERE SongID IN (SELECT SongID FROM "main.Songs" WHERE Posted IS NULL AND Confirmed IS NOT NULL ORDER BY RANDOM() LIMIT 1);'''
)

rows = cursor.fetchone()

try:
    r_songid = rows[0]
    r_artist = rows[1]
    r_title = rows[2]
    r_posted = rows[3]
except:
    print('> No suitable songs have been found in the database.')
    exit()

cursor.execute('''
    SELECT l.Link,lt.TypeName FROM "main.Links" AS l
    JOIN "main.LinkTypes" AS lt ON l.LinkTypeID = lt.LinkTypeID
    WHERE SongID = ? AND TypeName = "YouTube";''', (r_songid,)
)
r_links = cursor.fetchone()
r_link = r_links[0]

print(t.tweet(''+r_artist+' - '+r_title+'\n\n'+r_link))

cursor.execute(
    '''UPDATE "main.Songs"
    SET Posted = ?
    WHERE SongID = ?;''', (time.time(), r_songid)
)
conn.commit()
