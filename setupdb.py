import sqlite3

def create_table(db, create_table_sql):
    try:
        c = db.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

# Table create statements
roles = """CREATE TABLE IF NOT EXISTS roles (
            role	TEXT UNIQUE,
            roleid	INTEGER UNIQUE,
            emoji	TEXT UNIQUE,
            emojiid	INTEGER,
            PRIMARY KEY(roleid)
        )"""

epicGames = """CREATE TABLE IF NOT EXISTS epicGames (
                game	TEXT,
                slug	TEXT,
                url	TEXT,
                end_date	TEXT
            )"""

def main():
    con = sqlite3.connect('bot.db')
    create_table(con, roles)
    create_table(con,epicGames)

if __name__ == '__main__':
    main()