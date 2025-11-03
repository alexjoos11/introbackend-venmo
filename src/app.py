import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"

@app.route("/api/users/", methods=["GET"])
def get_users():
    """
    Endpoint for getting all users
    """
    return json.dumps({"users": DB.get_all_users}),200


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)

    if (name is None) or (username is None):
        return json.dumps({"error":"Bad request: Missing 'name' or 'username' in body"}), 400
    
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error":"Something went wrong while creating the user"}), 400
    return json.dumps(user), 201


@app.route("/api/user/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    """
    Endpoint for getting a specific user by ID
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error":"User not found"}), 404
    return json.dumps(user), 200


@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a specific user by ID
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error":"User not found"}), 404
    DB.delete_user_by_id(user_id)
    
    return json.dumps(user), 200


@app.route("/api/send/", methods=["POST"])
def send_money():
    """
    Endpoint for sending money from one user to another
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")

    #valid request check
    if sender_id is None or receiver_id is None or amount is None:
        return json.dumps({"error":"Bad request: Missing 'sender_id', 'receiver_id', or 'amount' in body"}), 400

    #users exist check
    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if sender is None:
        return json.dumps({"error":"Sender not found"}), 404
    if receiver is None:
        return json.dumps({"error":"Receiver not found"}), 404
    
    #valid balance check
    
    sender_balance = sender.get("balance", 0)
    if sender_balance - amount < 0:
        return json.dumps({"error":"Insufficient balance"}), 400
    if amount <= 0:
        return json.dumps({"error":"Invalid amount"}), 400

    DB.transfer_balance_by_id(sender_id, receiver_id, amount)
    
    return json.dumps({
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": amount 
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
