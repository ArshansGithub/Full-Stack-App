url = "baseurlhere"
function logout() {
    fetch(url + "/api/v1/logout", {
        method: "POST",
        credentials: "include"
    })
    .then(response => {
        if (response.ok) {
            window.location.href = "/";
        } else if (response.headers.get("content-type").includes("application/json")) {
            return response.json().then(data => alert(data.message));
        } else {
            alert("Something went wrong! Error code: " + response.status);
        }
    })
    .catch(error => {
        alert("Something went wrong! Error: " + error.message);
    });
}

function decide(lol) {
    if (cleared) {
        // Refresh apge
        window.location.href = "/dashboard";
    } else {
        load_user(lol);
    }
}

function load_user(alreadyLoaded = false) {
    const d = document.getElementById("date-picker")
    if (d == null) {
        return;
    };
    const req = new XMLHttpRequest();
    req.open("GET", url + "/api/v1/chipotle/user");
    req.withCredentials = true;
    req.onload = function () {
        if (req.status === 200) {
            let jsonResponse = JSON.parse(
                req.response.replace(/'/g, '"').replace(/True/g, 'true').replace(/False/g, 'false')
            );

            if (!alreadyLoaded) {
                Object.entries(jsonResponse).forEach(([key, value]) => {

                    if (Object.keys(value).length === 0) {
                        const req2 = new XMLHttpRequest();
                        req2.open("DELETE", url + "/api/v1/chipotle/user");
                        req2.withCredentials = true;
                        req2.setRequestHeader("Content-Type", "application/json");
                        req2.onload = function () {
                            if (!req2.status === 200) {
                                console.log("Something went wrong! (ln 75) Error code: " + req2.status);
                                return;
                            }
                        };
                        req2.send('{"type": "timestamp", "timestamp": "' + key + '"}');
                    } else {
                        const datestring = new Date(key).toLocaleString("en-US", {year: "numeric", "month": "numeric", "day": "numeric", hour: 'numeric', minute: 'numeric', hour12: true }).replaceAll('/', '-').replaceAll(',', '');
                        d.innerHTML += `<option value="${key}">${datestring}</option>`;
                    }
                   
                    
                });
                if (document.getElementById("date-picker").length <= 1) {
                    dd = document.getElementById("date-picker")
                    if (dd == null) {
                        return;
                    }
                    const newEle = document.createElement("p")
                    newEle.innerHTML = "You have not been assigned any codes yet. Sorry!"
                    dd.parentNode.replaceChild(newEle, dd)
                    cleareverything();
                }
            } else if (req.response.includes("No token provided") || req.response.includes("Invalid token")) {
                alert("Your session has expired. Please log in again.");
                window.location.href = "/";
            } else {
                d.innerHTML = `<option value="0" selected="">Select a date</option>`;

                Object.entries(jsonResponse).forEach(([key, value]) => {
                    if (Object.keys(value).length === 0) {
                        // Delete from server
                        const req2 = new XMLHttpRequest();
                        req2.open("DELETE", url + "/api/v1/chipotle/user");
                        req2.withCredentials = true;
                        req2.setRequestHeader("Content-Type", "application/json");
                        req2.onload = function () {
                            if (!req2.status === 200) {
                                console.log("Something went wrong! (ln 75) Error code: " + req2.status);
                                return;
                            }
                        };
                        req2.send('{"type": "timestamp", "timestamp": "' + key + '"}');
                        
                    } else {
                        const datestring = new Date(key).toLocaleString("en-US", {year: "numeric", "month": "numeric", "day": "numeric", hour: 'numeric', minute: 'numeric', hour12: true }).replaceAll('/', '-').replaceAll(',', '');
                        d.innerHTML += `<option value="${key}">${datestring}</option>`;
                    }
                    
                });

                document.querySelector(".list-container").innerHTML = "";
                itemsPerPage = 0;
                currentPage = 1;

                document.querySelector(".codes").style.display = "none";
                document.querySelector(".removeme").style.display = "block";
                if (document.getElementById("date-picker").length <= 1) {
                    dd = document.getElementById("date-picker")
                    if (dd == null) {
                        return;
                    }
                    const newEle = document.createElement("p")
                    newEle.innerHTML = "You have not been assigned any codes yet. Sorry!"
                    dd.parentNode.replaceChild(newEle, dd)
                    cleareverything();
                }
            }
        } else if (req.getResponseHeader("content-type") === "application/json") {
            let jsonResponse = JSON.parse(req.response);
            if (jsonResponse.error === "Username does not own any codes") {
                const d = document.getElementById("date-picker")
                if (d == null) {
                    return;
                };
                const newEle = document.createElement("p");
                newEle.innerHTML = "You have not been assigned any codes yet. Sorry!";
                d.parentNode.replaceChild(newEle, d);
                cleareverything();
            } else {
                alert(jsonResponse.error);
            }
        } else {
            alert("Something went wrong! Error code: " + req.status);
        }
    };
    req.send();

}

function copyCode(toCopy) {
    const toCheck = "Score! Use this code at checkout for a free Chipotle burrito: "
    if (toCopy.includes(toCheck)) {
        toCopy = toCopy.replace(toCheck, '').split(". Order:")[0];
        navigator.clipboard.writeText(toCopy);
    } else {
        navigator.clipboard.writeText(toCopy);
    }
    alert("Copied to clipboard!");
}

function saveUsed() {
    const selectedValue = document.getElementById('date-picker').value;

    if (selectedValue === "0") {
        alert("Please select a date!");
        return;
    }

    const req = new XMLHttpRequest();
    req.open("GET", url + "/api/v1/chipotle/user");
    req.withCredentials = true;
    req.onload = function() {
        if (req.status === 200) {
            const jsonResponse = JSON.parse(req.response.replace(/'/g, '"').replace(/True/g, 'true').replace(/False/g, 'false'));
            const responses = [];

            for (const [key, value] of Object.entries(jsonResponse[selectedValue])) {
                const isChecked = document.getElementById(key).checked;
                if (isChecked !== value.used) {
                    const req2 = new XMLHttpRequest();
                    req2.open("PUT", url + "/api/v1/chipotle/user");
                    req2.withCredentials = true;
                    req2.setRequestHeader("Content-Type", "application/json");
                    req2.onload = function() {
                        responses.push(req2.status);
                        if (req2.status !== 200) {
                            handleErrorResponse(req2);
                        }
                    };
                    
                    req2.send(JSON.stringify({"timestamp": selectedValue, "code": key}));
                }
            }
            
            if (responses.every((val) => val === 200)) {
                alert("Successfully updated codes!");
            
            }
            
        } else if (req.response.includes("No token provided") || req.response.includes("Invalid token")) {
            alert("Your session has expired. Please log in again.");
            window.location.href = "/";
        } else {
            handleErrorResponse(req);
        }
    };
    req.send();
}

function handleErrorResponse(req) {
    if (req.getResponseHeader("content-type") === "application/json") {
        const error = JSON.parse(req.response).error;
        alert(error === "Username, timestamp, or code does not exist" ? "This is a bug, please report it to the developer." : error);
    } else {
        alert("Something went wrong! Error code: " + req.status);
        console.error(req.response)
    }
}

function delCode(toDelete, timestamp) {
    const req = new XMLHttpRequest();
    req.open("DELETE", url + "/api/v1/chipotle/user");
    req.withCredentials = true;
    req.onload = function() {
        if (req.status === 200) {
            alert("Successfully deleted code!");
            document.getElementById(toDelete).parentElement.remove();
            if (document.querySelector(".list-container").length === "" || document.querySelector(".list-container").length === null) {
                decide(true);
            }

        } else if (req.response.includes("No token provided") || req.response.includes("Invalid token")) {
            alert("Your session has expired. Please log in again.");
            window.location.href = "/";
        } else {
            handleErrorResponse(req);
        }
    }
    req.setRequestHeader("Content-Type", "application/json");
    
    req.send(JSON.stringify({"timestamp": timestamp, "code": toDelete, "type": "code"}));
}

function deleteDate() {
    const selectedValue = document.getElementById('date-picker').value;

    if (selectedValue === "0") {
        alert("Please select a date!");
        return;
    }

    const req = new XMLHttpRequest();
    req.open("DELETE", url + "/api/v1/chipotle/user");
    req.withCredentials = true;
    req.onload = function() {
        if ((req.status === 400 && req.response.includes("Username does not own any codes")) || req.status === 200) {
            alert("Successfully deleted date!");
            window.location.href = "/dashboard";

        } else if (req.response.includes("No token provided") || req.response.includes("Invalid token")) {
            alert("Your session has expired. Please log in again.");
            window.location.href = "/";
        } else {
            console.error(req.response)
            alert("Something went wrong! Error code: " + req.status);
        }
    }
    req.setRequestHeader("Content-Type", "application/json");
    req.send(JSON.stringify({"timestamp": selectedValue, "type": "timestamp"}));
}

function selectDate () {

    const selectedValue = document.getElementById('date-picker').value;
    if (selectedValue == "0") {
        document.getElementsByClassName('list-container')[0].innerHTML = '';
        itemsPerPage = 0;
        currentPage = 1;

        document.getElementsByClassName('codes')[0].style.display = 'none';
        document.getElementsByClassName('removeme')[0].style.display = 'block';

        return;
    }

    const req = new XMLHttpRequest();
    req.open("GET", url + "/api/v1/chipotle/user");
    req.withCredentials = true;
    req.onload = function() {
        if (req.status == 200) {
            resp = req.response.replace(/'/g, '"').replace(/True/g, 'true').replace(/False/g, 'false')

            jsonResponse = JSON.parse(resp);

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
                input.innerHTML = key;
                input.checked = value['used'];
                input.id = key;
                
                const span = document.createElement('span');
                span.className = 'checkmark';
                const iterator = document.createElement('p');

                iterator.innerHTML = Object.keys(jsonResponse[selectedValue]).indexOf(key) + 1;
                iterator.style = 'margin-right:10px;'
                const span2 = document.createElement('span');
                span2.className = 'label-text';
                span2.innerHTML = key;

                const div = document.createElement('div');
                div.className = 'controls';
                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete-button';
                deleteButton.innerHTML = 'Delete';
                deleteButton.onclick = function () {delCode(key, selectedValue)};
                const copyButton = document.createElement('button');
                copyButton.className = 'copy-button';
                copyButton.innerHTML = '📋';
                copyButton.onclick = function () {copyCode(key)};

                label.appendChild(input);
                label.appendChild(iterator);
                label.appendChild(span);
                label.appendChild(span2);


                div.appendChild(copyButton);
                div.appendChild(deleteButton);
                firstDiv.appendChild(label);
                firstDiv.appendChild(div);
                document.querySelector('.list-container').appendChild(firstDiv);


            }

            document.querySelector('.codes').style.display = 'block';
            document.getElementsByClassName('removeme')[0].style.display = 'none';

            calculateItemsPerPage();

        } else if (req.response.includes("No token provided") || req.response.includes("Invalid token")) {
            alert("Your session has expired. Please log in again.");
            window.location.href = "/";
        } else if (req.getResponseHeader("content-type") == "application/json") {
            if (JSON.parse(req.response).error == "Username does not own any codes") {
                d = document.getElementById("date-picker")
                if (d == null) {
                    return;
                }
                const newEle = document.createElement("p")
                newEle.innerHTML = "You have not been assigned any codes yet. Sorry!"
                d.parentNode.replaceChild(newEle, d)
                cleareverything();
            } else {
                alert(JSON.parse(req.response).error);
            }
        } else {
            alert("Something went wrong! Error code: " + req.status);
        }
    };
    req.send();
}

function refreshCodes() {
    const selectedValue = document.getElementById('date-picker').value;
    if (selectedValue == "0") {
        document.getElementsByClassName('list-container')[0].innerHTML = '';
        itemsPerPage = 0;
        lastHeight = 0;
        currentPage = 1;

        document.getElementsByClassName('codes')[0].style.display = 'none';
        document.getElementsByClassName('removeme')[0].style.display = 'block';

        return;
    }

    // Get the list of all codes
    const req = new XMLHttpRequest();
    req.open("GET", url + "/api/v1/chipotle/user");
    req.withCredentials = true;
    req.onload = function() {
        if (req.status == 200) {
            resp = req.response.replace(/'/g, '"').replace(/True/g, 'true').replace(/False/g, 'false')

            jsonResponse = JSON.parse(resp);

            // Clear the list container
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
                input.innerHTML = key;
                input.checked = value['used'];
                input.id = key;
                
                const span = document.createElement('span');
                span.className = 'checkmark';
                const iterator = document.createElement('p');
                // Iterator is used to keep track of the number of codes based on the index of the key
                iterator.innerHTML = Object.keys(jsonResponse[selectedValue]).indexOf(key) + 1;
                iterator.style = 'margin-right:10px;'
                const span2 = document.createElement('span');
                span2.className = 'label-text';
                span2.innerHTML = key;

                const div = document.createElement('div');
                div.className = 'controls';
                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete-button';
                deleteButton.innerHTML = 'Delete';
                deleteButton.onclick = function () {delCode(key, selectedValue)};
                const copyButton = document.createElement('button');
                copyButton.className = 'copy-button';
                copyButton.innerHTML = '📋';
                copyButton.onclick = function () {copyCode(key)};

                label.appendChild(input);
                label.appendChild(iterator);
                label.appendChild(span);
                label.appendChild(span2);


                div.appendChild(copyButton);
                div.appendChild(deleteButton);
                firstDiv.appendChild(label);
                firstDiv.appendChild(div);
                document.querySelector('.list-container').appendChild(firstDiv);


            }
            // Set the display of the list container to be visible
            document.querySelector('.codes').style.display = 'block';
            document.getElementsByClassName('removeme')[0].style.display = 'none';
            // Calculate the initial itemsPerPage
            lastHeight = 0;
            calculateItemsPerPage();

            
        } else if (req.response.includes("No token provided") || req.response.includes("Invalid token")) {
            alert("Your session has expired. Please log in again.");
            window.location.href = "/";
        } else if (req.getResponseHeader("content-type") == "application/json") {
            if (JSON.parse(req.response).error == "Username does not own any codes") {
                d = document.getElementById("date-picker")
                if (d == null) {
                    return;
                }
                const newEle = document.createElement("p")
                newEle.innerHTML = "You have not been assigned any codes yet. Sorry!"
                d.parentNode.replaceChild(newEle, d)
                cleareverything();
            } else {
                alert(JSON.parse(req.response).error);
            }
        } else {
            alert("Something went wrong! Error code: " + req.status);
        }
    };
    req.send();

}

function cleareverything() {
    // Clear everything in the list container
    document.querySelector('.list-container').innerHTML = '';
    // Reset the items per page
    itemsPerPage = 0;
    // Reset the current page
    currentPage = 1;
    // Reset the display of the list container to be hidden
    document.querySelector('.codes').style.display = 'none';
    document.getElementsByClassName('removeme')[0].style.display = 'block';
    document.getElementsByClassName('select')[0].style.display = 'none';
    document.getElementsByClassName('select')[1].style.display = 'none';
    document.getElementsByClassName('setting')[1].style.display = 'none';
    cleared = true;
}

function calculateItemsPerPage() {
    const listContainer = document.querySelector('.list-container');
    const codeItems = document.querySelectorAll('.code-item');
    if (!lastHeight == 0) {
        if (Math.abs(lastHeight - Math.max(window.innerHeight, listContainer.clientHeight)) > 50) {
            lastHeight = Math.max(window.innerHeight, listContainer.clientHeight);
            return;
        } else {
            lastHeight = Math.max(window.innerHeight, listContainer.clientHeight);
        }
    }
    // Check if container height has changed significantly, if it hasnt then dont recalculate

    let containerHeight;

    containerHeight = Math.max(window.innerHeight, listContainer.clientHeight - 100);

    const codeHeight = codeItems.length > 0 ? codeItems[0].clientHeight : 0;

    // Calculate the number of items that fit in one page
    itemsPerPage = Math.floor(containerHeight / codeHeight);

    // Update the current page based on the new items per page
    if (detectMob()) {
        itemsPerPage = 4
    }
    showPage(currentPage);
}


function showPage(pageNumber) {
    const pages = document.querySelectorAll('.code-item');
    const totalPages = Math.ceil(pages.length / itemsPerPage);
    

    if (pageNumber < 1) {
        pageNumber = 1;
    } else if (pageNumber > totalPages) {
        pageNumber = totalPages;
    }

    currentPage = pageNumber;

    pages.forEach((page, index) => {
        if (index >= (pageNumber - 1) * itemsPerPage && index < pageNumber * itemsPerPage) {
            page.style.display = 'block';
        } else {
            page.style.display = 'none';
        }
    });

    // Update the page number at the top
    
    if (detectMob()) {
        console.log("MOBILELEE")
        document.getElementById('page-number').innerHTML = 'Page ' + pageNumber + ' of ' + totalPages + '<br></br><br></br>';
        document.getElementById('code-number').innerHTML = `Total codes: ${pages.length}<br></br><br></br>`
    } else {
        document.getElementById('page-number').innerHTML = 'Page ' + pageNumber + ' of ' + totalPages;
        document.getElementById('code-number').innerHTML = `Total codes: ${pages.length}`
        
    }
    
    if (totalPages == 1) {
        // Disable buttons if there is only one page
        document.getElementsByClassName("prev")[0].disabled = true;
        document.getElementsByClassName("next")[0].disabled = true;
    }
}
function detectMob() {
    console.log(window.innerHeight)
    console.log(window.innerWidth)
    return ( ( window.innerWidth <= 500 ) && ( window.innerHeight <= 900 ) );
}

function prevPage() {
    showPage(currentPage - 1);
}

function nextPage() {
    showPage(currentPage + 1);
}

function exportStuff() {
    // Check if valid date
    const date = document.getElementById('date-picker').value;
    
    // get selected value text
    const daText = document.getElementById("date-picker").options[document.getElementById("date-picker").selectedIndex].text.replace(":", "-")

    if (date == '0') {
        alert('Please select a date!');
        return;
    }

    const exportType = document.getElementById('exporter').value;
    const exportRes = document.getElementById('exporter2').value;
    const exportused = document.getElementById('exporter3').value;
    const exportFilter = document.getElementById('exporter4').value;
    const toCheck = "Score! Use this code at checkout for a free Chipotle burrito: "
    let toExport = ""
    const codes = document.querySelectorAll('.code-item');

    codes.forEach((code, index) => {
        if (code.style.display == 'block') {
            if (exportFilter == '1') {
                if (!code.querySelector('input').checked) {
                    return;
                }
            } else if (exportFilter == '2') {
                if (code.querySelector('input').checked) {
                    return;
                }
                
            }
            if (exportRes == '0') {
                toExport += code.querySelector('input').value;
            } else if (exportRes == '1') {
                if (code.querySelector('input').value.includes(toCheck)) {
                    toExport += code.querySelector('input').value.replace(toCheck, '').split(". Order:")[0];
                } else {
                    toExport += code.querySelector('input').value;
                }
            }
            if (exportused == '0') {
                toExport += " | Used: " + code.querySelector('input').checked.toString() + '\n'
            } else if (exportused == '1') {
                toExport += '\n'
            } else {
                alert('How did you get here lol. Report this. 2');
            }
            
        }
    });
    if (exportType == '0') {
        download(toExport, 'codes ' + daText + '.txt', 'text/plain');
        alert('Codes exported!')
    } else if (exportType == '1') {
        // Copy to clipboard
        navigator.clipboard.writeText(toExport);
        alert('Codes copied to clipboard!')
    } else {
        alert('How did you get here lol. Report this.');
    }

}

function download(text, name, type) {
    const a = document.createElement("a");
    const file = new Blob([text], {type: type});
    a.href = URL.createObjectURL(file);
    a.download = name;
    a.click();
}

// On page load, run the start function
window.addEventListener('load', load_user);
// JavaScript to control pagination
let currentPage = 1;
let itemsPerPage = 0;
let lastHeight = 0;
cleared = false;
// Update the itemsPerPage when the window is resized
window.addEventListener('resize', calculateItemsPerPage);
window.addEventListener('load', calculateItemsPerPage);