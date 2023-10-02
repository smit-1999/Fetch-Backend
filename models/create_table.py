import sqlite3
from sqlite3 import Error
def create_points_table():
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect('./database.db')
        c = conn.cursor()
        c.execute('''
                    CREATE TABLE IF NOT EXISTS points
                    ([id] INTEGER PRIMARY KEY AUTOINCREMENT,
                    [payer] TEXT,
                    [points] INTEGER,
                    [timestamp] DATETIME)
                ''')
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()