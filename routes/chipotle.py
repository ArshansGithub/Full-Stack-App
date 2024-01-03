import json, datetime, base64

from flask import request
from flask import Response, jsonify

from bson.json_util import dumps
from bson.json_util import loads

from database import db
import routes.auth as auth

def get_codes(admin: bool = True):
    collection = db['chipotle']
    if admin:
        # Return all codes
        raw = collection.find()
        toReturn = {}
        for document in raw:
            print(document)
            document.pop("_id")
            toReturn.update(document)
            
        
        if toReturn:
            return Response(dumps(toReturn).replace(r"\\u002e", r"."), status=200, mimetype='application/json')
        else:
            return Response('{"success": false, "error": "No codes found"}', status=400, mimetype='application/json')
    else:
        token = request.cookies.get("token")
        if not token:
            return Response('{"success": false, "error": "No token provided"}', status=400, mimetype='application/json')
        
        decoded = auth.verify_jwt_token(token)
        username = decoded.get("username")

        # Find user's codes where their username is the key in the collection
        try:
            data = collection.find_one({username: {"$exists": True}})[username]
        except TypeError:
            data = None

        if data:
            return Response(dumps(data).replace(r"\\u002e", r"."), status=200, mimetype='application/json')
        else:
            return Response('{"success": false, "error": "Username does not own any codes"}', status=400, mimetype='application/json')

    
def del_user_code():
    if "timestamp" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No timestamp provided"}', status=400, mimetype='application/json')
    elif "code" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No code provided"}', status=400, mimetype='application/json')
    
    # Decode token and make sure username matches
    token = request.cookies.get("token")
    decoded = auth.verify_jwt_token(token)
    username = decoded.get("username")
    
    collection = db['chipotle']
    
    try:
        timestamp = dict(request.get_json())["timestamp"]
        code = dict(request.get_json())["code"].replace(r".", r"\u002e")

        # Delete the specified code under the given username and timestamp
        result = collection.update_one(
            {username + "." + timestamp + "." + code: {"$exists": True}},
            {"$unset": {f"{username}.{timestamp}.{code}": ""}}
        )

        if result.matched_count == 0:
            return Response('{"success": false, "error": "Username, timestamp, or code does not exist"}', status=400, mimetype='application/json')
        
        return get_codes(admin=False)  # Assuming get_codes() is the function to retrieve codes for non-admin users
    except Exception as e:
        print(e)
        return Response('{"success": false, "error": "Failed to delete code"}', status=500, mimetype='application/json')
    
def set_used():
    # Set a code to used based on username, timestamp, and code
    if "timestamp" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No timestamp provided"}', status=400, mimetype='application/json')
    elif "code" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No code provided"}', status=400, mimetype='application/json')
    
    # Decode token and make sure username matches
    token = request.cookies.get("token")
    decoded = auth.verify_jwt_token(token)
    username = decoded.get("username")
    timestamp = dict(request.get_json())["timestamp"]
    code = dict(request.get_json())["code"].replace(r".", r"\u002e")
    #print(code)
    
    collection = db['chipotle']
    #print(timestamp)
    try:
        currentStatus = collection.find_one({username: {"$exists": True}})[username][timestamp][code]['used']
        print(currentStatus)
    except:
        return Response('{"success": false, "error": "Username, timestamp, or code does not exist"}', status=400, mimetype='application/json')
    
    # Set code to used
    try:
        

        # Update the "used" status of the specified code under the given username and timestamp
        if currentStatus:
            result = collection.update_one(
                {username + "." + timestamp + "." + code: {"$exists": True}},
                {"$set": {f"{username}.{timestamp}.{code}.used": False}}
            )
        else:
            result = collection.update_one(
                {username + "." + timestamp + "." + code: {"$exists": True}},
                {"$set": {f"{username}.{timestamp}.{code}.used": True}}
            )
        if result.matched_count == 0:
            return Response('{"success": false, "error": "Username, timestamp, or code does not exist"}', status=400, mimetype='application/json')
        
        return get_codes(admin=False)  # Assuming get_codes() is the function to retrieve codes for non-admin users
    except Exception as e:
        print(e)
        return Response('{"success": false, "error": "Failed to set code to used"}', status=500, mimetype='application/json')
    
def add_codes():
    collection = db['chipotle']
    if "codes" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No codes provided"}', status=400, mimetype='application/json')

    if "user" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No user provided"}', status=400, mimetype='application/json')
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    codesToAdd = {}
    for code in dict(request.get_json())["codes"].split("\n"):
        codesToAdd[code.replace(r".", r"\u002e")] = {"used": False}
    
    # Insert the codes into the "unsorted" sub-document of "chipotle" collection
    try:
        #collection.update_one({}, {"$set": {f"unsorted.{now}": codesToAdd}}, upsert=True)
        collection.update_one({}, {"$set": {f"{request.get_json()['user']}.{now}": codesToAdd}}, upsert=True)
        return get_codes(admin=True)
    except Exception as e:
        print(e)
        return Response('{"success": false, "error": "Failed to add codes"}', status=500, mimetype='application/json')

def del_codes():
    collection = db['chipotle']
    
    if "timestamp" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No timestamp provided"}', status=400, mimetype='application/json')
    elif "type" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No type provided"}', status=400, mimetype='application/json')
        
    token = request.cookies.get("token")
    decoded = auth.verify_jwt_token(token)
    username = decoded.get("username")
    timestamp = dict(request.get_json())["timestamp"]
    wutToDo = dict(request.get_json())["type"]
    # Check if the username exists in the 'chipotle' collection
    try:
        data = collection.find_one({username + "." + timestamp: {"$exists": True}})
        print(data)
    except TypeError as e:
        return Response('{"success": false, "error": "Timestamp does not exist"}', status=400, mimetype='application/json')
    
    if not data:
        return Response('{"success": false, "error": "Something does not exist"}', status=400, mimetype='application/json')
    print(wutToDo)
    if wutToDo == "timestamp":
        # Delete a specific timestamp and its associated codes for the given username
        try:
            # Add to history
            collection.update_one({}, {"$set": {f"history.{timestamp}": data[username][timestamp]}}, upsert=True)
            collection.update_one({username: {"$exists": True}}, {"$unset": {f"{username}.{timestamp}": ""}})

            return get_codes(admin=False)  # Assuming get_codes() is the function to retrieve codes for admins
        except Exception as e:
            print(e)
            return Response('{"success": false, "error": "Failed to delete codes"}', status=500, mimetype='application/json')
    elif wutToDo == "code":
        # Delete a specific code for the given username and timestamp
        if "code" not in dict(request.get_json()):
            return Response('{"success": false, "error": "No code provided"}', status=400, mimetype='application/json')
        
        code = dict(request.get_json())["code"].replace(r".", r"\u002e")
        
        # Check if the code exists in the 'chipotle' collection under the given username and timestamp
        try:
            daCheck = collection.find_one({username + "." + timestamp + "." + code: {"$exists": True}})
        except:
            return Response('{"success": false, "error": "Code not found"}', status=400, mimetype='application/json')
        
        if not daCheck:
            return Response('{"success": false, "error": "Code does not exist"}', status=400, mimetype='application/json')
        
        try:
            # Add to history
            collection.update_one({}, {"$set": {f"history.{timestamp}.{code}": data[username][timestamp][code]}}, upsert=True)
            
            collection.update_one({username + "." + timestamp: {"$exists": True}}, {"$unset": {f"{username}.{timestamp}.{code}": ""}})
            
            # Check if the timestamp doesnt have any codes
            data = collection.find_one({username + "." + timestamp: {"$exists": True}})
            if not data:
                # Delete the timestamp if it has no codes
                collection.update_one({username: {"$exists": True}}, {"$unset": {f"{username}.{timestamp}": ""}})
                
            return get_codes(admin=False)  # Assuming get_codes() is the function to retrieve codes for admins
        except Exception as e:
            print(e)
            return Response('{"success": false, "error": "Failed to delete code"}', status=500, mimetype='application/json')
        
"""def sort_codes():
    collection = db['chipotle']
    
    if "username" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No username provided"}', status=400, mimetype='application/json')
    elif "timestamp" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No timestamp provided"}', status=400, mimetype='application/json')
    elif "amount" not in dict(request.get_json()):
        return Response('{"success": false, "error": "No amount provided"}', status=400, mimetype='application/json')
    
    timestamp = dict(request.get_json())["timestamp"]
    amount = dict(request.get_json())["amount"]
    username = dict(request.get_json())["username"]
    
    try:
        data = collection.find_one({"unsorted." + timestamp: {"$exists": True}})["unsorted"][timestamp]
    except TypeError:
        return Response('{"success": false, "error": "Timestamp does not exist"}', status=400, mimetype='application/json')
        
    if not data:
        return Response('{"success": false, "error": "Timestamp does not exist: 2"}', status=400, mimetype='application/json')
    
    # Check if the amount is a valid integer
    if not isinstance(amount, int) or amount <= 0 or amount > len(data):
        return Response(f'{{"success": false, "error": "Improper amount given", "amount": {len(data)}}}', status=400, mimetype='application/json')
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get the codes to be sorted
    codes_to_sort = data
    codes_to_move = {code: codes_to_sort[code] for code in list(codes_to_sort.keys())[:amount]}
    
    # Update 'history' and 'username' fields with the sorted codes
    try:
        collection.update_one({}, {"$set": {f"history.{now}": codes_to_move}}, upsert=True)
        collection.update_one({}, {"$set": {f"{username}.{now}": codes_to_move}}, upsert=True)
        
        # Remove the sorted codes from 'unsorted' field
        collection.update_one({}, {"$unset": {f"unsorted.{timestamp}": ""}})
        
        return get_codes(admin=True)  # Assuming get_codes() is the function to retrieve codes for admins
    except Exception as e:
        print(e)
        return Response('{"success": false, "error": "Failed to sort codes"}', status=500, mimetype='application/json')"""
