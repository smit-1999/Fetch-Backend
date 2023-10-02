from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/add', methods=['POST'])
def add_to_points():
    json = request.get_json()
    if 'payer' not in json:
        return "Missing payer in request", 500

    if 'points' not in json:
        return "Missing points in request", 500

    if 'timestamp' not in json:
        return "Missing timestamp in request", 500
     
    payer=json['payer']
    points=json['points']
    timestamp=json['timestamp']

    conn = sqlite3.connect('./database.db')
    try:
        c = conn.cursor()
        c.execute("INSERT INTO points (payer,points,timestamp) VALUES (?, ?, ?)", (payer, points, timestamp))
        conn.commit()
        conn.close()
        print('in main')

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return "Successfully added point",200

if __name__ == "__main__":

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
        print('Exception found',e)
    finally:
        if conn:
            print('closed conn in main')
            conn.close()
    app.run(host='127.0.0.1',port=8000)  
