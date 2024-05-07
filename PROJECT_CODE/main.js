//const http = require('http'); // no longer needed, as we are now using https
const https = require('https');
const fs = require('fs');
const ip = require('ip');

const port = 8080;

 // Map URL paths to corresponding file paths
 const routes = {
    '/': 'index.html',
    '/temperature': 'temperature.html',
    '/humidity': 'humidity.html',
    '/pressure': 'pressure.html',
    '/light': 'light.html',
    '/display': 'display.html',
    '/gas': 'gas.html',
    '/mic': 'mic.html',
    '/mic/record': 'record.html',
    '/style/style.css': 'style/style.css',
    '/script/script.js': 'script/script.js',
    '/favicon.ico': 'favicon.ico'
};

// Determine content type based on file extension
const contentTypeMap = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.ico': 'image/x-icon'
};
function serve(req, res) {
    const url = req.url;

    // Handle requests
    if (url in routes) {
        const filePath = routes[url];
        const contentType = getContentType(filePath);

        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                console.log(`Error reading file ${filePath}: ${err}`);
                res.writeHead(404, {'Content-Type': 'text/html'});
                res.write("<h1>404 Not Found</h1>");
                res.end();
            } else {
                res.writeHead(200, {'Content-Type': contentType});
                res.write(data);
                res.end();
            }
        });
    } else {
        res.writeHead(404, {'Content-Type': 'text/html'});
        res.write("<h1>404 Not Found</h1>");
        res.end();
    }
}

function getContentType(filePath) {
    const ext = filePath.split('.').pop();
    return contentTypeMap[`.${ext}`] || 'text/html';
}

//http.createServer((req, res) => {
//    serve(req, res);
//}).listen(port);
//no longer needed, as we are now using https
https.createServer({
    key: fs.readFileSync('raspberrypi-fr.local.key'),
    cert: fs.readFileSync('raspberrypi-fr.local.crt'),
    passphrase: '3153'
}, (req, res) => {
    serve(req, res);
}).listen(port+1);
console.log(`Server running at http://${ip.address()}:${port}/`);
console.log(`Server running at https://${ip.address()}:${port+1}/`);
