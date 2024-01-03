import json
from flask import request, Response
from database import db

def get_users():
    collection = db['accounts']
    users = list(collection.find({}, {"_id": 0, "password": 0}))
    return Response(json.dumps(users), status=200, mimetype='application/json')

def check_user(user):
    collection = db['accounts']
    return collection.find_one({"username": user}) is not None

def del_user():
    data = dict(request.get_json())

    if "username" not in data:
        return Response('{"success": false, "error": "No username provided"}', status=400, mimetype='application/json')
    elif not check_user(data["username"]):
        return Response('{"success": false, "error": "User does not exist"}', status=400, mimetype='application/json')

    collection = db['accounts']
    collection.delete_one({"username": data["username"]})

    return get_users()

def verify_user(verify=False):
    data = dict(request.get_json())

    if "username" not in data:
        return Response('{"success": false, "error": "No username provided"}', status=400, mimetype='application/json')
    elif not check_user(data["username"]):
        return Response('{"success": false, "error": "User does not exist"}', status=400, mimetype='application/json')

    collection = db['accounts']
    user_data = collection.find_one({"username": data["username"]})

    if user_data["verified"] and verify:
        return Response('{"success": false, "error": "User is already verified"}', status=400, mimetype='application/json')
    elif not user_data["verified"] and not verify:
        return Response('{"success": false, "error": "User is already NOT verified"}', status=400, mimetype='application/json')

    collection.update_one({"username": data["username"]}, {"$set": {"verified": verify}})
    return get_users()
