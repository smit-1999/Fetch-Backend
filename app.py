import sqlite3
from flask import Flask, request
from sqlite3 import Error
from routes.add_points import add_points
from routes.check_balance import check_balance
from routes.spend_points import spend_points


app = Flask(__name__)

@app.route('/add', methods=['POST'])
def add_to_points():
    return add_points(request.get_json())

@app.route('/balance', methods=['GET'])
def check_balance_points():
    return check_balance()

@app.route('/spend', methods=['POST'])
def spend_some_points():
    return spend_points(request.get_json())
     

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
        print(e)
    finally:
        if conn:
            conn.close()
    app.run(host='127.0.0.1',port=8000)  
