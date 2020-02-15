import sqlite3

def setup():
    with sqlite3.connect('taki.db') as db:
        db.execute(
            '''CREATE TABLE IF NOT EXISTS "main.Songs"(
            SongID INTEGER PRIMARY KEY,
            Artist TEXT,
            Title TEXT,
            Posted REAL DEFAULT NULL,
            User INTEGER,
            Timestamp INTEGER
            );'''
        )
        db.execute(
            '''CREATE TABLE IF NOT EXISTS "main.Links"(
            LinkID INTEGER PRIMARY KEY,
            Link TEXT,
            LinkTypeID INTEGER,
            SongID INTEGER
            );'''
        )
        db.execute(
            '''CREATE TABLE IF NOT EXISTS "main.LinkTypes"(
            LinkTypeID INTEGER PRIMARY KEY,
            TypeName TEXT,
            Regex TEXT
            );'''
        )

        db.execute(
            '''CREATE TABLE IF NOT EXISTS "main.Auth"(
            UserID INTEGER PRIMARY KEY,
            User INTEGER,
            Level INTEGER
            );'''
        )

        db.execute(
            '''INSERT INTO "main.LinkTypes" (
            TypeName,
            Regex
            )
            VALUES (
            "YouTube",
            "(http(s)://)?(www\\.)?(youtube.com/watch\\?v=|youtu.be/)(.*)"
            );'''
        )
        db.commit()
    return 'Database setup complete.'

print(setup())
