from flask import Flask, request
from models.create_table import create_points_table
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
    create_points_table()
    app.run(host='127.0.0.1',port=8000)  
