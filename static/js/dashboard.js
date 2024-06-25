const url = "http://192.168.0.164:5000";

async function logout() {
    try {
        const response = await fetch(url + "/api/v1/logout", {
            method: "POST",
            credentials: "include"
        });

        await handleResponse(response, {
            200: () => { window.location.href = "/"; }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

function decide(lol) {
    if (cleared) {
        window.location.href = "/dashboard";
    } else {
        load_user(lol);
    }
}

async function load_user(alreadyLoaded = false) {
    const d = document.getElementById("date-picker");
    if (!d) return;

    try {
        const response = await fetch(url + "/api/v1/chipotle/user", { credentials: "include" });

        await handleResponse(response, {
            200: async (jsonResponse) => {
                if (!alreadyLoaded) {
                    await populateUserDates(jsonResponse, d);
                } else {
                    alert("Your session has expired. Please log in again.");
                    window.location.href = "/";
                }
            }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

async function populateUserDates(jsonResponse, d) {
    Object.entries(jsonResponse).forEach(async ([key, value]) => {
        if (Object.keys(value).length === 0) {
            const req2 = await fetch(url + "/api/v1/chipotle/user", {
                method: "DELETE",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ type: "timestamp", timestamp: key })
            });
            if (req2.status !== 200) {
                console.log("Something went wrong! (ln 75) Error code: " + req2.status);
            }
        } else {
            const datestring = new Date(key).toLocaleString("en-US", {
                year: "numeric", month: "numeric", day: "numeric",
                hour: "numeric", minute: "numeric", hour12: true
            }).replaceAll('/', '-').replaceAll(',', '');
            d.innerHTML += `<option value="${key}">${datestring}</option>`;
        }
    });
    if (d.length <= 1) {
        const newEle = document.createElement("p");
        newEle.innerHTML = "You have not been assigned any codes yet. Sorry!";
        d.parentNode.replaceChild(newEle, d);
        cleareverything();
    }
}

function copyCode(toCopy) {
    const toCheck = "Score! Use this code at checkout for a free Chipotle burrito: ";
    if (toCopy.includes(toCheck)) {
        toCopy = toCopy.replace(toCheck, '').split(". Order:")[0];
    }
    navigator.clipboard.writeText(toCopy);
    alert("Copied to clipboard!");
}

async function saveUsed() {
    const selectedValue = document.getElementById('date-picker').value;
    if (selectedValue === "0") {
        alert("Please select a date!");
        return;
    }

    try {
        const response = await fetch(url + "/api/v1/chipotle/user", { credentials: "include" });

        await handleResponse(response, {
            200: async (jsonResponse) => {
                const responses = await updateUsedCodes(jsonResponse, selectedValue);
                if (responses.every((val) => val === 200)) {
                    alert("Successfully updated codes!");
                }
            }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

async function updateUsedCodes(jsonResponse, selectedValue) {
    const responses = [];

    for (const [key, value] of Object.entries(jsonResponse[selectedValue])) {
        const isChecked = document.getElementById(key).checked;
        if (isChecked !== value.used) {
            const req2 = await fetch(url + "/api/v1/chipotle/user", {
                method: "PUT",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ timestamp: selectedValue, code: key })
            });
            responses.push(req2.status);
            if (req2.status !== 200) {
                handleErrorResponse(req2);
            }
        }
    }

    return responses;
}

async function handleErrorResponse(req) {
    if (req.headers.get("content-type").includes("application/json")) {
        const error = await req.json();
        alert(error === "Username, timestamp, or code does not exist" ? "This is a bug, please report it to the developer." : error);
    } else {
        alert("Something went wrong! Error code: " + req.status);
        console.error(req.response);
    }
}

async function delCode(toDelete, timestamp) {
    try {
        const response = await fetch(url + "/api/v1/chipotle/user", {
            method: "DELETE",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ timestamp: timestamp, code: toDelete, type: "code" })
        });

        await handleResponse(response, {
            200: () => {
                alert("Successfully deleted code!");
                document.getElementById(toDelete).parentElement.remove();
                if (!document.querySelector(".list-container").innerHTML) {
                    decide(true);
                }
            }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

async function deleteDate() {
    const selectedValue = document.getElementById('date-picker').value;
    if (selectedValue === "0") {
        alert("Please select a date!");
        return;
    }

    try {
        const response = await fetch(url + "/api/v1/chipotle/user", {
            method: "DELETE",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ timestamp: selectedValue, type: "timestamp" })
        });

        await handleResponse(response, {
            200: () => {
                alert("Successfully deleted date!");
                window.location.href = "/dashboard";
            },
            400: async () => {
                const text = await response.text();
                if (text.includes("Username does not own any codes")) {
                    alert("Successfully deleted date!");
                    window.location.href = "/dashboard";
                } else {
                    alert("Something went wrong! Error code: " + response.status);
                }
            }
        });
    } catch (error) {
        alert("Something went wrong! Error: " + error.message);
    }
}

async function selectDate() {
    const selectedValue = document.getElementById('date-picker').value;
    if (selectedValue === "0") {
        document.getElementsByClassName('list-container')[0].innerHTML = '';
        itemsPerPage = 0;
        currentPage = 1;

        document.getElementsByClassName('codes')[0].style.display = 'none';
        document.getElementsByClassName('removeme')[0].style.display = 'block';

        return;
    }

    try {
        const response = await fetch(url + "/api/v1/chipotle/user", { credentials: "include" });

        await handleResponse(response, {
            200: (jsonResponse) => {
                document.querySelector('.list-container').innerHTML = '';

                for (const [key, value] of Object.entries(jsonResponse[selectedValue])) {
                    const firstDiv = document.createElement('div');
                    firstDiv.className = 'code-item';
                    const label = document.createElement('label');
                    label.className = 'label-text';
                    const input = document.createElement('input');
                    input.name = 'code-checkbox';
                    input.type = 'checkbox';
                    input.value = key;
                    input.checked = value['used'];
                    input.id = key;

                    const span = document.createElement('span');
                    span.className = 'checkmark';
                    const iterator = document.createElement('p');
                    iterator.innerHTML = Object.keys(jsonResponse[selectedValue]).indexOf(key) + 1;
                    iterator.style = 'margin-right:10px;';
                    const span2 = document.createElement('span');
                    span2.className = 'label-text';
                    span2.innerHTML = key;

                    const div = document.createElement('div');
                    div.className = 'controls';
                    const deleteButton = document.createElement('button');
                    deleteButton.className = 'delete-button';
                    deleteButton.innerHTML = 'Delete';
                    deleteButton.onclick = function () { delCode(key, selectedValue); };
                    const copyButton = document.createElement('button');
                    copyButton.className = 'copy-button';
                    copyButton.innerHTML = '📋';
                    copyButton.onclick = function () { copyCode(key); };

                    label.appendChild(input);
                    label.appendChild(iterator);
                    label.appendChild(span);
                    label.appendChild(span2);
                    div.appendChild(deleteButton);
                    div.appendChild(copyButton);
                    firstDiv.appendChild(label);
                    firstDiv.appendChild(div);
                    document.querySelector('.list-container').appendChild(firstDiv);
                }
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
