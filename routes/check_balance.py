import sqlite3
from sqlite3 import Error
def check_balance():
    conn = sqlite3.connect('./database.db')
    try:
        c = conn.cursor()
        c.execute("SELECT payer,SUM(points) as totalPoints FROM points GROUP BY payer")
        res={}
        myresult = c.fetchall()
        for x in myresult:
            if x[0] not in res:
                res[x[0]] = x[1]
            else:
                res[x[0]] += x[1]

    except Error as e:
        print(e)
        return e,500
    finally:
        conn.close()
    return res