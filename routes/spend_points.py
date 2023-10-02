import sqlite3

def spend_points(req):
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