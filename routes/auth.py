from flask import request
from flask import Response
from flask import make_response, render_template, redirect, jsonify
from database import db, secret_key
import jwt
import bcrypt, json, datetime, base64
import binascii
from geopy.geocoders import Nominatim
from geopy.timezone import Timezone
import pytz, requests

whitelist = []
expiry = 3600
iplogs = "webhook here"    

def generate_jwt_token(username, ips, second=expiry):
    now = datetime.datetime.utcnow()
    expiration = now + datetime.timedelta(seconds=second)
    payload = {
        "username": username,
        'exp': expiration,
        'iat': now,
        'ip': ips
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Check user ip
        userIP = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        accountIPS = payload["ip"]
        if userIP not in accountIPS:
            return None
        return payload
    except jwt.ExpiredSignatureError as e:
        return None
    except jwt.DecodeError as e:
        return None
    
def protection(admin=False):
    try:
        if "token" not in request.cookies:
            return Response('{"success": false, "message": "No token provided"}', status=400, mimetype='application/json')
    except Exception:
        return Response('{"success": false, "message": "No token detected"}', status=400, mimetype='application/json')

    if not check_token(request.cookies.get("token"), admin):
        resp = Response('{"success": false, "message": "Invalid token OR you do not have access to this action"}', status=400, mimetype='application/json')
        resp.delete_cookie("token")
        return resp

    return False

def logout():
    if "token" not in request.cookies:
        return Response('{"success": false, "message": "No token provided"}', status=400, mimetype='application/json')

    token = request.cookies.get("token")
    decoded = verify_jwt_token(token)
    if decoded is None:
        return Response('{"success": false, "message": "Invalid token"}', status=400, mimetype='application/json')
    username = decoded.get("username")

    collection = db['sessions']
    collection.delete_one({"username": username})

    resp = Response('{"success": true, "message": "Logged out"}', status=200, mimetype='application/json')
    resp.delete_cookie("token")
    return resp

def check_token(original_token, admin):
    decodedToken = verify_jwt_token(original_token)
    if decodedToken is None: 
        print("idk")
        return False

    user = decodedToken.get("username")
    
    collection = db['sessions']
    accounts = db['accounts']
    session_data = collection.find_one({"username": user})

    if session_data is None or session_data["token"] != original_token:
        print("doenst match")
        return False
    
    # Check user ip
    userIP = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    accountIPS = accounts.find_one({"username": user})["ip"]
    if userIP not in accountIPS:
        print("wrong ip")
        return False
    
    # Convert expiry epoch to datetime
    expiry_date = datetime.datetime.utcfromtimestamp(decodedToken["exp"]).strftime("%Y-%m-%d %H:%M:%S.%f")
    if expiry_date != session_data["expiry"]:
        print("expired")
        return False

    if datetime.datetime.utcnow() > datetime.datetime.strptime(expiry_date, "%Y-%m-%d %H:%M:%S.%f"):
        collection.delete_one({"username": user})
        return False

    if admin:
        return session_data["admin"]

    return True

def do_login_flow(account, second=expiry):
    checkSecurity = checkUserIP(request, account["username"], increment=False)
    if checkSecurity:
        return checkSecurity

    collection = db['sessions']
    userIp = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    token = generate_jwt_token(account["username"], [userIp], second)
    epoch = verify_jwt_token(token)["exp"]
    expiry_date = datetime.datetime.utcfromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S.%f")
    new_session_data = {"username": account["username"], "token": token, "expiry": str(expiry_date), "admin": account["admin"]}

    # Find the user's session data in the sessions collection
    session_data = collection.find_one({"username": account["username"]})

    if session_data is None:
        # If session data doesn't exist, insert a new session entry
        collection.insert_one(new_session_data)
    else:
        # If session data exists, update the existing session data
        collection.update_one({"username": account["username"]}, {"$set": new_session_data})

    resp = redirect("/dashboard", code=302)
    resp.set_cookie('token', token, max_age=second, httponly=True)
    return resp


def update_db(info):
    # Replace 'accounts' with the name of the accounts collection
    collection = db['accounts']
    collection.insert_one(info)

def check_db(user):
    # Replace 'accounts' with the name of the accounts collection
    collection = db['accounts']
    result = collection.find_one({"username": user})
    return result is not None

def register():
    return Response('{"message": "Disabled"}', 410)
    data = dict(request.get_json())

    # Check if the request has the required fields
    if "username" not in data or "password" not in data or "type" not in data:
        return Response(status=400)

    data["username"] = data["username"].lower()

    if check_db(data["username"]):
        return Response('{"success": false, "message": "Username already exists"}', status=400, mimetype='application/json')

    # Check if the type is valid
    if data["type"] == "password":
        byte_password = bytes(data["password"], "utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(byte_password, salt)

        update_db({"username": data["username"], "verified": False, "admin": False, "type": "password", "password": hashed.decode("utf-8"), "ip": [request.environ.get('HTTP_X_REAL_IP', request.remote_addr)]})

        return Response('{"success": true}', status=200, mimetype='application/json')

    elif data["type"] == "question": # Don't use for now
        if "question" not in data:
            return Response(status=400)

        byte_password = bytes(data["question"] + "^|||^" + data["password"], "utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(byte_password, salt)

        update_db({"username": data["username"], "verified": False, "admin": False, "type": "question", "password": hashed.decode("utf-8"), "ip": [request.environ.get('HTTP_X_REAL_IP', request.remote_addr)]})

        return Response('{"success": true}', status=200, mimetype='application/json')

    else:
        return Response(status=400)

def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = f'\nIP: {ip_address}\nCity: {response.get("city")}\nRegion: {response.get("region")}\nCountry: {response.get("country_name")}\nOrg: {response.get("org")}\n\n'
    return location_data
        
def checkUserIP(request, username, increment=True):
    userIP = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if userIP is None:
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nUsername: {username}\n"
        
        dataToSend += "Special Message: Invalid IP```"
        
        req = requests.post(iplogs, headers={"Content-Type": "application/json"}, json={"content": dataToSend})
        resp = Response('{"success": false, "message": "Invalid IP"}', status=400, mimetype='application/json')
        resp.set_cookie('token', "", max_age=0, httponly=True)
        return resp
    
    if userIP in whitelist:
        return False
    
    accountCollection = db['accounts']
    
    # Check if the user's IP is in the accounts document
    listOfIps = accountCollection.find_one({"username": username})
    print(listOfIps)
    if not listOfIps:
        return Response('{"success": false, "message": "Invalid username"}', status=403, mimetype='application/json')
    
    if userIP not in listOfIps["ip"]:
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nUsername: {username}\n"
        print(dataToSend)
        if userIP != None:
            try:
                locationData = get_location(userIP)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {userIP}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
            
        dataToSend += "Special Message: IP address not in list of IPs```"
        
        req = requests.post(iplogs, headers={"Content-Type": "application/json"}, json={"content": dataToSend})
        
        resp = Response('{"success": false, "message": "Invalid IP"}', status=403, mimetype='application/json')
        resp.set_cookie('token', "", max_age=0, httponly=True)
        return resp
    
    securityCollection = db['security']
    
    user_timezone = pytz.timezone('US/Pacific')
    
    currentAttempts = securityCollection.find_one({"ip": userIP})
    if currentAttempts is not None:
        # Calculate additional cooldown if necessary
        extra_attempts = max(0, currentAttempts["attempts"] - 5)
        additional_cooldown = datetime.timedelta(minutes=5 * (extra_attempts // 5))
        
        # Check if the original 5-minute window has passed
        original_cooldown_expired = currentAttempts["lastAttempt"] < datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        
        # Reset attempts to 1 if the original 5-minute window has passed
        if original_cooldown_expired:
            securityCollection.update_one({"ip": userIP}, {"$set": {"attempts": 1}})
        elif increment:
            # Increment attempts if within the original 5-minute window
            update_data = {
                "$set": {"ip": userIP, "lastAttempt": datetime.datetime.utcnow()},
                "$inc": {"attempts": 1}
            }
            securityCollection.update_one({"ip": userIP}, update_data, upsert=True)
    else:
        # Create new entry if no attempts exist
        securityCollection.insert_one({"ip": userIP, "attempts": 1, "lastAttempt": datetime.datetime.utcnow()})
    
    # Calculate unlock time with local timezone (PST)
    if currentAttempts and currentAttempts["attempts"] >= 5 and currentAttempts["lastAttempt"] >= datetime.datetime.utcnow() - datetime.timedelta(minutes=5):
        total_attempts_with_cooldown = currentAttempts["attempts"] + (currentAttempts["attempts"] - 1) // 5
        cooldown_multiplier = (total_attempts_with_cooldown - 1) // 5
        cooldown_duration = datetime.timedelta(minutes=5 * cooldown_multiplier)
        unlock_time_utc = currentAttempts["lastAttempt"] + cooldown_duration
        unlock_time_local = unlock_time_utc.replace(tzinfo=pytz.UTC).astimezone(user_timezone)
        unlock_time_formatted = unlock_time_local.strftime("%m/%d/%Y %I:%M %p")
        
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nUsername: {username}\n"

        if userIP != None:
            try:
                locationData = get_location(userIP)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {userIP}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
            
        dataToSend += f"Special Message: Too many attempts try again after: {unlock_time_formatted} (PST)```"
        
        req = requests.post(iplogs, headers={"Content-Type": "application/json"}, json={"content": dataToSend})
        
        return Response('{"success": false, "message": "Too many failed login attempts. Please try again after ' + unlock_time_formatted + ' (PST)."}', status=400, mimetype='application/json')
    
    return False



    
def login():
    data = dict(request.get_json())

    # Check if the request has the required fields
    if "username" not in data or "password" not in data or "type" not in data:
        return Response(status=400)

    data["username"] = data["username"].lower()

    # Replace 'accounts' with the name of the accounts collection
    collection = db['accounts']
    account = collection.find_one({"username": data["username"]})

    if account is not None:
        checkSecurity = checkUserIP(request, data["username"])
        if checkSecurity:
            return checkSecurity
        if account["type"] == "password":
            if bcrypt.checkpw(bytes(data["password"], "utf-8"), bytes(account["password"], "utf-8")) and account["verified"]:
                if account["admin"]:
                    if "seconds" not in data:
                        return do_login_flow(account)
                    return do_login_flow(account, data["seconds"])
                else:
                    return do_login_flow(account)
            else:
                return Response('{"success": false, "message": "Incorrect password OR account not verified"}', status=400, mimetype='application/json')

        elif account["type"] == "question":
            if "question" not in data:
                return Response(status=400)

            if bcrypt.checkpw(bytes(data["question"] + "^|||^" + data["password"], "utf-8"), bytes(account["password"], "utf-8")) and account["verified"]:
                if bcrypt.checkpw(bytes(data["password"], "utf-8"), bytes(account["password"], "utf-8")) and account["verified"]:
                    if account["admin"]:
                        if "seconds" not in data:
                            return do_login_flow(account)
                        return do_login_flow(account, data["seconds"])
                    else:
                        return do_login_flow(account)
                else:
                    return Response('{"success": false, "message": "Incorrect answer OR account not verified."}', status=400, mimetype='application/json')

        else:
            return Response('{"success": false, "message": "Invalid account type"}', status=400, mimetype='application/json')
        
    checkSecurity = checkUserIP(request, data["username"])
    if checkSecurity:
        return checkSecurity
    return Response('{"success": false, "message": "Username does not exist"}', status=400, mimetype='application/json')