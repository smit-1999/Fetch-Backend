from flask import Flask, request
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

def handle_deduction(req):
    points =  - 1 * req['points']
    payer = req['payer']
    conn = sqlite3.connect('./database.db')
    try:
        c = conn.cursor()
        c.execute("""SELECT SUM(points) as total FROM Points WHERE payer = ?""", (payer,))

        total = c.fetchall()
        if total[0][0] < points :
            return "No points available to subtract", 500

        c.execute("""
            WITH PrefixSum AS ( SELECT *, SUM(points) OVER (ORDER BY timestamp) AS totalPoints FROM Points WHERE payer = ?) 
            SELECT * FROM ( 
                SELECT id, payer, points,timestamp FROM PrefixSum WHERE totalPoints<= ? AND points>0 ORDER BY timestamp
            )
            UNION     
            SELECT * FROM (
                SELECT  id, payer, points,timestamp FROM PrefixSum WHERE totalPoints>= ? AND points>0 ORDER BY timestamp LIMIT 1
            )
            ORDER BY timestamp;""",(payer,points,points))
        
        allPossiblePayers = c.fetchall()
        updated_rows = []
        for row in allPossiblePayers:
            if points <= 0 or row[2] <= 0:
                updated_rows.append([row[0],row[1],row[2],row[3]])
            else:
                deduct_points = min(points, row[2])
                updatedPoints = row[2] - deduct_points
                points -= deduct_points
                updated_rows.append([row[0],row[1],updatedPoints,row[3]])

        for row in updated_rows:
            c.execute("""UPDATE Points
                    set points = ?
                    WHERE id = ?; """,(row[2], row[0]))
            conn.commit()
        
        conn.close()
        return "Successfully added negative point",200
    except Error as e:
        print(e)
        return e,500
    finally:
        if conn:
            conn.close()

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

    if points < 0:
        return handle_deduction(json)

    print('is error here')
    conn = sqlite3.connect('./database.db')
    try:
        c = conn.cursor()
        c.execute("INSERT INTO points (payer,points,timestamp) VALUES (?, ?, ?)", (payer, points, timestamp))
        conn.commit()
        conn.close()

    except Error as e:
        print(e)
        return e,500
    finally:
        if conn:
            conn.close()

    return "Successfully added point",200

@app.route('/balance', methods=['GET'])
def check_balance():
    conn = sqlite3.connect('./database.db')
    try:
        c = conn.cursor()
        c.execute("SELECT payer,SUM(points) as totalPoints FROM points GROUP BY payer")
        res={}
        myresult = c.fetchall()
        for x in myresult:
            print(x)
            if x[0] not in res:
                res[x[0]] = x[1]
            else:
                res[x[0]] += x[1]

    except Error as e:
        print(e)
        return e,500
    finally:
        #do nothing1
        a=1
    return res

@app.route('/spend', methods=['POST'])
def spend_points():
    req = request.get_json()
    if 'points' not in req:
        return "Missing points parameter",500
    
    to_spend = req['points']
    conn = sqlite3.connect('./database.db')
    c = conn.cursor()
    c.execute("SELECT SUM(points) as totalUserPoints FROM points")
    totalUserPoints = 0
    myresult = c.fetchall()
    for x in myresult:
        totalUserPoints = x[0]
    
    if totalUserPoints < to_spend:
        return  "User does not have enough points to spend", 400
    
    c.execute("""
              WITH PrefixSum AS ( SELECT *, SUM(points) OVER (ORDER BY timestamp) AS totalPoints FROM Points) 
            SELECT * FROM ( 
              SELECT id, payer, points,timestamp FROM PrefixSum WHERE totalPoints<=? AND points>0 ORDER BY timestamp
              )
            UNION
            SELECT * FROM (
                SELECT id, payer, points,timestamp FROM PrefixSum WHERE totalPoints>=? AND points>0 ORDER BY timestamp LIMIT 1
            )
            ORDER BY timestamp""",(to_spend,to_spend))
    allPossiblePayers = c.fetchall()

    res={}
    updated_rows = []
    for row in allPossiblePayers:
        if to_spend <= 0 or row[2] <= 0:
            updated_rows.append([row[0],row[1],row[2],row[3]])
        else:
            deduct_points = min(to_spend, row[2])
            updatedPoints = row[2] - deduct_points
            to_spend -= deduct_points
            if row[1] in res:
                res[row[1]] += -deduct_points
            else:
                res[row[1]] = -deduct_points
            updated_rows.append([row[0],row[1],updatedPoints,row[3]])

    for row in updated_rows:
        c.execute("""UPDATE Points
                set points = ?
                WHERE id = ? AND payer = ?; """,(row[2], row[0], row[1]))
        conn.commit()
    
    conn.close()
    return res,200 

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
