url = "url here"
/*function register() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    var data = {
        username: username,
        password: password,
        type: "password"
    };

    const req = new XMLHttpRequest();
    req.open("POST", url + "/api/v1/register");
    req.setRequestHeader("Content-Type", "application/json");
    req.dataType = "json";
    req.onload = function() {
        console.log()
        if (req.status == 200) {
            alert("Success");
        } else if (req.getResponseHeader("content-type") == "application/json") {
            alert(JSON.parse(req.response).message);
        } else {
            alert("Something went wrong! Error code: " + req.status);
        }
    };
    req.send(JSON.stringify(data));
}*/

function login() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    var data = {
        username: username,
        password: password,
        type: "password"
    };

    const req = new XMLHttpRequest();
    req.open("POST", url + "/api/v1/login");
    req.setRequestHeader("Content-Type", "application/json");
    req.dataType = "json";
    req.withCredentials = true;
    req.onload = function() {
        if (req.status == 200) {
            window.location.href = req.responseURL;
        } else if (req.getResponseHeader("content-type") == "application/json") {
            alert(JSON.parse(req.response).message);
        } else {
            alert("Something went wrong! Error code: " + req.status);
        }
    };
    req.send(JSON.stringify(data));
}

