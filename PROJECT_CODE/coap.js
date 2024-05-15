//COAP SERVER

const coap = require("coap");
const fetch = require("node-fetch");

const coapPort = 5683;
const httpServerUrl = "http://raspberrypi-fr.local:8050";

const coapServer = coap.createServer(function (req, res) {
    console.log("Request received");

    if (req.method === "POST") {
        handlePostRequest(req, res);
    } else {
        handleNonPostRequest(req, res);
    }
});

function handlePostRequest(req, res) {
    try {
        const url = `${httpServerUrl}${req.url}`;
        const payload = req.payload.toString();

        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: payload,
        };

        console.log("Sending POST request to HTTP server:", url);
        fetch(url, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error("HTTP request failed with status " + response.status);
                }
                console.log("Response from HTTP server:", response.status, response.statusText);
                return response.json();
            })
            .then(data => {
                res.setOption("Content-Format", "application/json");
                res.code = 200;
                res.end(JSON.stringify(data));
            })
            .catch(error => {
                console.error("Error in HTTP request:", error.message);
                res.setOption("Content-Format", "application/json");
                res.code = 500;
                res.end(JSON.stringify({ error: error.message }));
            });

    } catch (error) {
        console.error("Error processing request:", error.message);
        res.setOption("Content-Format", "application/json");
        res.code = 500;
        res.end(JSON.stringify({ error: error.message }));
    }
}

function handleNonPostRequest(req, res) {
    try {
        const url = `${httpServerUrl}${req.url}`;
        const requestOptions = {
            method: req.method, // Use the CoAP method as HTTP method
            headers: {
                'Content-Type': 'application/json',
            },
        };

        console.log(`Sending ${req.method} request to HTTP server:`, url);
        fetch(url, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error("HTTP request failed with status " + response.status);
                }
                console.log("Response from HTTP server:", response.status, response.statusText);
                return response.json();
            })
            .then(data => {
                res.setOption("Content-Format", "application/json");
                res.code = 200;
                res.end(JSON.stringify(data));
            })
            .catch(error => {
                console.error("Error in HTTP request:", error.message);
                res.setOption("Content-Format", "application/json");
                res.code = 500;
                res.end(JSON.stringify({ error: error.message }));
            });

    } catch (error) {
        console.error("Error processing request:", error.message);
        res.setOption("Content-Format", "application/json");
        res.code = 500;
        res.end(JSON.stringify({ error: error.message }));
    }
}

coapServer.listen(coapPort, () => {
    console.log(`CoAP Server started on port ${coapPort}`);
});
