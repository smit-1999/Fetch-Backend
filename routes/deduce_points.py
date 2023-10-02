import sqlite3
from sqlite3 import Error

def handle_deductions(req):
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