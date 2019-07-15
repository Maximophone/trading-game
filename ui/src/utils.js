import { API_ADDRESS } from "./config.js";
import openSocket from "socket.io-client";

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
    return fetch(API_ADDRESS + url, fetch_data).then((response) => response.json())
    .then(success).catch(error);
}

export function post(url, data, success, error){
    return request("POST", url, data, success, error);
}

export function get(url, success, error){
    return request("GET", url, null, success, error);
}

export function get_socket(){
    var socket = openSocket(API_ADDRESS);
    socket.on("connect", function(){
      socket.emit("connection", {data: "connected"}, function(sid){
        console.log(sid);
      });
    });
    return socket;
}

export function is_float(x){
    return !isNaN(x) && !(x == null)
}

export var Sides = {
    BUY: true,
    SELL: false,
}