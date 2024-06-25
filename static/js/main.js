const url = "http://192.168.0.164:5000";

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("Please fill in all fields!");
        return
    }

    const data = {
        username: username,
        password: password
    };

    try {
        const response = await fetch(url + "/api/v1/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        await handleResponse(response, {
            200: () => {
                alert("Success");
            }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;


    if (!username || !password) {
        alert("Please fill in all fields!");
        return
    }

    const data = {
        username: username,
        password: password
    };

    try {
        const response = await fetch(url + "/api/v1/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "include",
            body: JSON.stringify(data)
        });

        await handleResponse(response, {
            200: () => {
                window.location.href = response.url;
            },
            401: () => {
                window.location.replace('/');
                alert("Invalid session!")
            }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

async function handleResponse(response, handlers) {
    const contentType = response.headers.get("content-type");
    const text = await response.text();

    if (contentType && contentType.includes("text/html")) {
        handlers[response.status]();
        return;
    }

    const jsonData = JSON.parse(text);

    if (handlers[response.status]) {

        const jsonResponse = contentType && contentType.includes("application/json") ? await jsonData : null;
        handlers[response.status](jsonResponse);
    } else if (contentType && contentType.includes("application/json")) {
        alert(jsonData.message || "Something went wrong! Error code: " + response.status);
    } else {
        alert("Something went wrong! Error code: " + response.status);
    }
}
window.onload = function(){
    document.getElementById("register").onclick=async() => {
      await register();
    };
    document.getElementById("login").onclick=async() => {
      await login();
    };
};
