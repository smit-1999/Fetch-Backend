from sqlite3 import Error
import sqlite3
from routes.deduce_points import handle_deductions
def add_points(req):
    if 'payer' not in req:
        return "Missing payer in request", 500

    if 'points' not in req:
        return "Missing points in request", 500

    if 'timestamp' not in req:
        return "Missing timestamp in request", 500
     
    payer=req['payer']
    points=req['points']
    timestamp=req['timestamp']

    if points < 0:
        return handle_deductions(req)

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