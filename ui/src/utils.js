function request(method, url, data, success, error){
    var fetch_data
    if(method==="GET"){
        fetch_data = {
            method: method,
            credentials: "include",
        }
    } else {
        fetch_data = {
            method: method,
            credentials: "include",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'text/plain',
            },
            body: JSON.stringify(data),
        }
    }
    return fetch(url, fetch_data).then((response) => response.json())
    .then(success).catch(error);
}

export function post(url, data, success, error){
    return request("POST", url, data, success, error);
}

export function get(url, success, error){
    return request("GET", url, null, success, error);
}