from flask import Response
from flask import request
from flask import Flask
from flask import render_template, redirect, make_response, copy_current_request_context
from flask_cors import CORS
import requests, threading
import base64

import routes.auth as auth
import routes.home as home
import routes.admin as admin
import routes.chipotle as chipotle

def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = f'\nIP: {ip_address}\nCity: {response.get("city")}\nRegion: {response.get("region")}\nCountry: {response.get("country_name")}\nOrg: {response.get("org")}\n\n'
    return location_data

# Logging webhook
userWebhook = ""
baseWebhook = ""
adminWebhook = ""
authWebhook = ""

app = Flask(__name__)
CORS(app, supports_credentials=True)

api_base = "/api/v1"

# Home
@app.route("/")
def main():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('x-real-ip'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(baseWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report).start()
    if "token" in request.cookies:
        a = auth.protection()
        if a:
            return redirect("/dashboard")
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(authWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    a = auth.protection()
    if a:
        # Remove the cookie
        resp = make_response('<script>window.location.replace("/");</script>', 403)
        resp.set_cookie('token', '', expires=0)
        threading.Thread(target=report, args=("Attempted to go to dashboard but invalid",)).start()
        return resp
    
    username = auth.verify_jwt_token(request.cookies.get("token")).get("username")
    threading.Thread(target=report, args=("User going to dashboard: " + username,)).start()
    # Capitalize the first letter
    username = username[0].upper() + username[1:]

    return render_template('dashboard.html', username=username)

# Register
@app.route(api_base + "/register", methods=["POST"])
def register_acc():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(authWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted register: " + str(dict(request.get_json())),)).start()
    return auth.register()

# Login
@app.route(api_base + "/login", methods=["POST"])
def login_acc():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(authWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted login: " + str(dict(request.get_json())),)).start()
    return auth.login()

# Logout
@app.route(api_base + "/logout", methods=["POST"])
def logout_acc():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(authWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    a = auth.protection()
    if a:
        threading.Thread(target=report, args=("Attempted logout",)).start()
        return a
    # Get cookie
    token = request.cookies.get("token")
    threading.Thread(target=report, args=("Attempted logout: " + str(token),)).start()
    return auth.logout()

# Admin
@app.route(api_base + "/admin/users", methods=["GET"])
def get_users():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(adminWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to get users admin",)).start()
    a = auth.protection(admin=True)
    if a:
        return a
    return admin.get_users()

@app.route(api_base + "/admin/users", methods=["DELETE"])
def del_user():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(adminWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to del users admin",)).start()
    a = auth.protection(admin=True)
    if a:
        return a
    return admin.del_user()

@app.route(api_base + "/admin/users", methods=["PUT", "PATCH"])
def verify_user():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(adminWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to verify users admin",)).start()
    a = auth.protection(admin=True)
    if a:
        return a
    if request.method == "PUT":
        return admin.verify_user(verify=True)
    elif request.method == "PATCH":
        return admin.verify_user(verify=False)
    else:
        return Response('{"success": false, "error": "Invalid method"}', status=400, mimetype='application/json')

@app.route(api_base + "/chipotle/admin", methods=["GET"])
def get_codes():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(adminWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to get codes admin",)).start()
    a = auth.protection(admin=True)
    if a:
        return a
    return chipotle.get_codes(admin=True)

@app.route(api_base + "/chipotle/admin", methods=["POST"])
def add_codes():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(adminWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to add codes admin",)).start()
    a = auth.protection(admin=True)
    if a:
        return a
    return chipotle.add_codes()

@app.route(api_base + "/chipotle/admin", methods=["DELETE"])
def del_codes():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(adminWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to del codes admin",)).start()
    a = auth.protection(admin=True)
    if a:
        return a
    return chipotle.del_codes()

@app.route(api_base + "/chipotle/admin", methods=["PUT"])
def sort_codes():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(adminWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to sort codes admin",)).start()
    a = auth.protection(admin=True)
    if a:
        return a
    return "Not done"

@app.route(api_base + "/chipotle/user", methods=["PUT"])
def mark():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(userWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to mark codes user",)).start()
    a = auth.protection()
    if a:
        return a
    return chipotle.set_used()

@app.route(api_base + "/chipotle/user", methods=["GET"])
def get_user_code():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(userWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to get codes user",)).start()
    a = auth.protection()
    if a:
        return a
    return chipotle.get_codes(admin=False)

@app.route(api_base + "/chipotle/user", methods=["DELETE"])
def del_user_code():
    @copy_current_request_context
    def report(msg=None):
        # Check if cookie
        try:
            if "token" in request.cookies:
                cookie = request.cookies.get("token")
            else:
                cookie = "None"
        except:
            cookie = "None"
        ip = request.headers.get('x-real-ip')
        dataToSend = f"```Endpoint: {request.path}\nUser-Agent: {request.headers.get('User-Agent')}\nReferrer: {request.headers.get('Referer')}\nCookie: {cookie}\n" 
        
        if ip != None:
            try:
                locationData = get_location(ip)
                dataToSend += locationData
            except:
                dataToSend += f"IP: {ip}\nSomething went wrong getting location data"
        else:
            dataToSend += f"Error getting IP\n"
            # Try different methods of getting IP
            ip1 = str(request.headers.get('X-Forwarded-For'))
            ip2 = str(request.headers.get('X-Real-Ip'))
            dataToSend += f"Attempt 1: {ip1}\nAttempt 2: {ip2}\n"
        if msg:
            dataToSend += f"Special Message: {msg}\n```"
        else:
            dataToSend += f"```"
        req = requests.post(userWebhook, headers={"Content-Type": "application/json"}, json={"content": dataToSend})

    threading.Thread(target=report, args=("Attempted to del codes user",)).start()
    a = auth.protection()
    if a:
        return a
    return chipotle.del_codes()

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
