const url = "http://localhost:5000";

async function register() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

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
            }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

async function handleResponse(response, handlers) {
    const contentType = response.headers.get("content-type");

    if (handlers[response.status]) {
        const jsonResponse = contentType && contentType.includes("application/json") ? await response.json() : null;
        handlers[response.status](jsonResponse);
    } else if (contentType && contentType.includes("application/json")) {
        const jsonResponse = await response.json();
        alert(jsonResponse.message || "Something went wrong! Error code: " + response.status);
    } else {
        alert("Something went wrong! Error code: " + response.status);
    }
}
