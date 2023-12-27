// const http = require('http');
import http from 'http';
let counter = 0;
http.createServer((req, res) => {
    // Check the URL of the request
    if (req.url === '/events') {
        // Set the necessary headers for SSE
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
        res.setHeader('Access-Control-Allow-Origin', 'http://localhost:5173');
        res.setHeader('Access-Control-Allow-Methods', 'GET,POST,DELETE,PUT,OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type,Authorization');
        res.setHeader('Access-Control-Allow-Credentials', 'true');
        if (req.method === 'OPTIONS') {
            // 设置跨域头
            
            // res.writeHead(200);
            res.end();
            return;
        }

        // Send an event every second
        // The server time is: ${new Date().toLocaleTimeString()}
        const t = setInterval(() => {
            res.write(`data: ${JSON.stringify({
                time: new Date().toLocaleTimeString(),
                content: `counter:${counter}`,
            })}\n\n`);
            counter++;
            if (counter === 10) {
                counter = 0
                clearInterval(t);
                res.write(`data: [DONE]\n\n`);
                res.end()
            }
        }, 1000);
    } else {
        res.writeHead(404);
        res.end();
    }
}).listen(8000, () => {
    console.log('Server started on port 8000');
});