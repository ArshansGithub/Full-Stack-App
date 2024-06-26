import time

from flask import request
from flask import Response
from flask import make_response, render_template, redirect, jsonify
from database import db, secret_key
from main import buildResponse, getUserIP
import jwt
import bcrypt, json, datetime, base64
import binascii
from geopy.geocoders import Nominatim
from geopy.timezone import Timezone
import pytz, requests

expiry = 3600
iplogs = "webhook here"    

def generate_jwt_token(username, ips, second=expiry):
    now = time.time()
    expiration = now + second
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
        userIP = getUserIP()
        accountIPS = payload["ip"]
        if userIP not in accountIPS:
            return None
        return payload
    except jwt.ExpiredSignatureError as e:
        return None
    except jwt.DecodeError as e:
        return None
    
def protection(admin=False):
    if "token" not in request.cookies:
        return buildResponse(False, "No token provided", 400)

    if not check_token(request.cookies.get("token"), admin):
        return buildResponse(False, "Invalid token OR you do not have access to this action", 400, delete=True)

    return False

def logout():

    token = request.cookies.get("token")
    decoded = verify_jwt_token(token)
    if decoded is None:
        buildResponse(False, "Invalid token", 400, delete=True)

    username = decoded.get("username")

    collection = db['sessions']
    delete = collection.delete_one({"username": username})

    if delete.acknowledged:
        return buildResponse(True, "Logged out", 200, delete=True)

    return buildResponse(False, "Failed to log out", 400)

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
    userIP = getUserIP()
    accountIPS = accounts.find_one({"username": user})["ip"]

    if userIP not in accountIPS:
        print("wrong ip")
        return False
    
    # Convert expiry epoch to datetime
    expiry_date = decodedToken["exp"]
    if expiry_date != session_data["expiry"]:
        print("expired")
        return False

    # "%Y-%m-%d %H:%M:%S.%f"
    if time.time() > expiry_date:
        collection.delete_one({"username": user})
        return False

    if admin:
        return session_data["admin"]

    return True

def do_login_flow(account, second=expiry):

    collection = db['sessions']
    userIp = getUserIP()

    token = generate_jwt_token(account["username"], [userIp], second)
    epoch = verify_jwt_token(token)["exp"]
    new_session_data = {"username": account["username"], "token": token, "expiry": epoch, "admin": account["admin"]}

    # Find the user's session data in the sessions collection
    session_data = collection.find_one({"username": account["username"]})

    if session_data is None:
        # If session data doesn't exist, insert a new session entry
        insert = collection.insert_one(new_session_data)
        if not insert.acknowledged:
            return buildResponse(False, "Failed to insert session data", 400)
    else:
        # If session data exists, update the existing session data
        update = collection.update_one({"username": account["username"]}, {"$set": new_session_data})

        if not update.acknowledged:
            return buildResponse(False, "Failed to update session data", 400)

    resp = redirect("/dashboard", code=302)
    resp.set_cookie('token', token, max_age=second, httponly=True)
    return resp

def check_db(user):
    collection = db['accounts']
    result = collection.find_one({"username": user})
    return result is not None

def register():
    # return Response('{"message": "Disabled"}', 410)
    data = dict(request.get_json())

    # Check if the request has the required fields
    if "username" not in data or "password" not in data:
        return buildResponse(False, "Missing fields", 400)

    data["username"] = data["username"].lower()

    if check_db(data["username"]):
        return buildResponse(False, "Username already exists", 400)

    byte_password = bytes(data["password"], "utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(byte_password, salt)
    userIP = getUserIP()

    insert = db['accounts'].insert_one({"username": data["username"], "verified": False, "admin": False, "password": hashed.decode("utf-8"), "ip": [userIP]})

    if not insert.acknowledged:
        return buildResponse(False, "Failed to insert account", 400)

    return buildResponse(True, "Account created", 200)

def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = f'\nIP: {ip_address}\nCity: {response.get("city")}\nRegion: {response.get("region")}\nCountry: {response.get("country_name")}\nOrg: {response.get("org")}\n\n'
    return location_data

def checkUserIP(request, username, increment=True):
    userIP = getUserIP()

    if userIP is None:
        # dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nUsername: {username}\n"
        #
        # dataToSend += "Special Message: Invalid IP```"
        
        #requests.post(iplogs, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

        return buildResponse(False, "Invalid IP", 400, delete=True)
    
    accountCollection = db['accounts']
    
    # Check if the user's IP is in the accounts document
    listOfIps = accountCollection.find_one({"username": username})
    #print(listOfIps)

    if not listOfIps:
        return buildResponse(False, "Invalid username", 400, delete=True)

    if userIP not in listOfIps["ip"]:
        # Log later
        return buildResponse(False, "Invalid IP", 400, delete=True)
    
    securityCollection = db['security']

    currentAttempts = securityCollection.find_one({"ip": userIP})

    if currentAttempts is not None:
        # Calculate additional cooldown if necessary
        extra_attempts = max(0, currentAttempts["attempts"] - 5)
        #additional_cooldown = datetime.timedelta(minutes=5 * (extra_attempts // 5))
        
        # Check if the original 5-minute window has passed
        original_cooldown_expired = currentAttempts["lastAttempt"] < (time.time() - (5 * 60))
        
        # Reset attempts to 1 if the original 5-minute window has passed
        if original_cooldown_expired:
            update = securityCollection.update_one({"ip": userIP}, {"$set": {"attempts": 1}})
            if not update.acknowledged:
                return buildResponse(False, "Failed to reset attempts", 400, delete=True)
        elif increment:
            # Increment attempts if within the original 5-minute window
            update_data = {
                "$set": {"ip": userIP, "lastAttempt": time.time()},
                "$inc": {"attempts": 1}
            }
            update = securityCollection.update_one({"ip": userIP}, update_data, upsert=True)
            if not update.acknowledged:
                return buildResponse(False, "Failed to increment attempts", 400, delete=True)
    else:
        # Create new entry if no attempts exist
        insert = securityCollection.insert_one({"ip": userIP, "attempts": 1, "lastAttempt": time.time()})
        if not insert.acknowledged:
            return buildResponse(False, "Failed to insert new entry", 400, delete=True)
    
    # Calculate unlock time with local timezone (PST)
    if currentAttempts and currentAttempts["attempts"] >= 5 and currentAttempts["lastAttempt"] >= (time.time() - (5 * 60)):
        total_attempts_with_cooldown = currentAttempts["attempts"] + (currentAttempts["attempts"] - 1) // 5
        cooldown_multiplier = (total_attempts_with_cooldown - 1) // 5
        cooldown_duration_minutes = 5 * cooldown_multiplier
        unlock_time_epoch = currentAttempts["lastAttempt"] + (cooldown_duration_minutes * 60)

        # Convert unlock time to local timezone UTC
        unlock_time_formatted = datetime.datetime.utcfromtimestamp(unlock_time_epoch).strftime('%Y-%m-%d %H:%M:%S')

        # Log here
        return buildResponse(False, f"Too many failed login attempts. Please try again after {unlock_time_formatted} (UTC)", 400, delete=True)

    return False



    
def login():
    data = dict(request.get_json())

    data["username"] = data["username"].lower()

    checkSecurity = checkUserIP(request, data["username"])

    if checkSecurity:
        return checkSecurity

    # Check if the request has the required fields
    if "username" not in data or "password" not in data:
        return buildResponse(False, "Missing fields", 400)

    # Replace 'accounts' with the name of the accounts collection
    collection = db['accounts']
    account = collection.find_one({"username": data["username"]})

    if account is None:
        return buildResponse(False, "Username or password invalid", 400)

    matchingPassword = bcrypt.checkpw(bytes(data["password"], "utf-8"), bytes(account["password"], "utf-8"))

    if not matchingPassword:
        return buildResponse(False, "Username or password invalid", 400)

    if not account["verified"]:
        return buildResponse(False, "Account not verified", 400)

    return do_login_flow(account, expiry)

