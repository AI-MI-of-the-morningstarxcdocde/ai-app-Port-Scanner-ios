const http = require('http');
const fs = require('fs');
const path = require('path');

// Setup logging
const logFile = fs.createWriteStream(path.join(__dirname, 'nx_mcp_sse.log'), { flags: 'a' });
function logMessage(msg) {
  const timestamp = new Date().toISOString();
  const logString = `${timestamp} - ${msg}\n`;
  logFile.write(logString);
  console.log(msg);
}

// Create a status tracker to monitor connections
let connections = 0;
let lastConnectionTime = null;
const statusPath = path.join(__dirname, 'nx_mcp_status.json');

function updateStatus(connected = false) {
  if (connected) {
    connections++;
    lastConnectionTime = new Date().toISOString();
  }
  
  const status = {
    server: 'nx-mcp',
    status: 'running',
    port: 9686,
    connections,
    lastConnectionTime,
    startTime: startTime.toISOString(),
    uptime: Math.floor((Date.now() - startTime) / 1000) + ' seconds'
  };
  
  fs.writeFileSync(statusPath, JSON.stringify(status, null, 2));
  return status;
}

// HTML template for the landing page
const landingPageHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>nx-mcp Server</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
    h1 {
      color: #2c3e50;
    }
    .card {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 16px;
      font-weight: bold;
    }
    .status.running {
      background-color: #d4edda;
      color: #155724;
    }
    pre {
      background: #f1f1f1;
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
    }
    .button {
      display: inline-block;
      background: #4CAF50;
      color: white;
      padding: 8px 16px;
      text-decoration: none;
      border-radius: 4px;
      font-weight: bold;
    }
    #connectionTest {
      margin-top: 20px;
      padding: 15px;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <h1>nx-mcp Server</h1>
  
  <div class="card">
    <h2>Server Status</h2>
    <p><span class="status running">Running</span></p>
    <p>Server is listening on port 9686</p>
    <p>Endpoints available:</p>
    <ul>
      <li><code>/</code> - This landing page</li>
      <li><code>/sse</code> - Server-Sent Events endpoint</li>
      <li><code>/status</code> - JSON status information</li>
      <li><code>/health</code> - Health check endpoint</li>
    </ul>
  </div>
  
  <div class="card">
    <h2>Connection Test</h2>
    <button onclick="testConnection()" class="button">Test SSE Connection</button>
    <div id="connectionTest"></div>
  </div>
  
  <div class="card">
    <h2>Server Information</h2>
    <pre id="serverInfo">Loading server information...</pre>
  </div>
  
  <script>
    // Fetch server status
    fetch('/status')
      .then(response => response.json())
      .then(data => {
        document.getElementById('serverInfo').textContent = JSON.stringify(data, null, 2);
      })
      .catch(error => {
        document.getElementById('serverInfo').textContent = 'Error fetching server information: ' + error.message;
      });
    
    // Function to test SSE connection
    function testConnection() {
      const testDiv = document.getElementById('connectionTest');
      testDiv.innerHTML = '<p>Connecting to SSE endpoint...</p>';
      
      try {
        const evtSource = new EventSource('/sse');
        
        evtSource.onopen = function() {
          testDiv.innerHTML += '<p style="color: green">✓ Connection established!</p>';
        };
        
        evtSource.onmessage = function(event) {
          testDiv.innerHTML += '<p><strong>Message received:</strong> ' + event.data + '</p>';
        };
        
        evtSource.onerror = function() {
          testDiv.innerHTML += '<p style="color: red">× Error in connection</p>';
          evtSource.close();
        };
        
        // Close connection after 5 seconds
        setTimeout(() => {
          evtSource.close();
          testDiv.innerHTML += '<p>Test completed - Connection closed</p>';
        }, 5000);
      } catch (error) {
        testDiv.innerHTML += '<p style="color: red">× Error: ' + error.message + '</p>';
      }
    }
  </script>
</body>
</html>
`;

// Track server start time
const startTime = new Date();
// Initialize status
updateStatus();

// Create an SSE server on port 9686
const server = http.createServer((req, res) => {
  logMessage(`Received request: ${req.method} ${req.url}`);
  
  // Handle different routes
  if (req.url === '/sse') {
    // SSE endpoint
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });
    
    // Send an initial message
    const initialMessage = { type: 'connection', status: 'connected', time: new Date().toISOString() };
    res.write(`data: ${JSON.stringify(initialMessage)}\n\n`);
    logMessage('SSE connection established');
    updateStatus(true);
    
    // Keep the connection alive with periodic heartbeat messages
    const intervalId = setInterval(() => {
      const heartbeatMsg = { type: 'heartbeat', timestamp: Date.now() };
      res.write(`data: ${JSON.stringify(heartbeatMsg)}\n\n`);
      logMessage('Sent heartbeat message');
    }, 10000);
    
    // Handle client disconnect
    req.on('close', () => {
      clearInterval(intervalId);
      logMessage('Client disconnected from SSE');
    });
  } else if (req.url === '/health') {
    // Health check endpoint
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', timestamp: Date.now() }));
    logMessage('Health check request served');
  } else if (req.url === '/status') {
    // Status endpoint
    res.writeHead(200, { 'Content-Type': 'application/json' });
    const status = updateStatus();
    res.end(JSON.stringify(status));
    logMessage('Status request served');
  } else if (req.url === '/') {
    // Landing page
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(landingPageHtml);
    logMessage('Landing page served');
  } else {
    // 404 for any other paths
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('404 Not Found');
    logMessage(`404 for path ${req.url}`);
  }
});

// Error handling for the server
server.on('error', (err) => {
  logMessage(`Server error: ${err.message}`);
  if (err.code === 'EADDRINUSE') {
    logMessage('Port already in use, retrying in 5 seconds...');
    setTimeout(() => {
      server.close();
      server.listen(9686);
    }, 5000);
  }
});

// Start the server
server.listen(9686, '0.0.0.0', () => {
  logMessage('NX MCP Server running on port 9686');
});

// Handle process termination
process.on('SIGINT', () => {
  logMessage('Received SIGINT, shutting down server...');
  server.close();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logMessage('Received SIGTERM, shutting down server...');
  server.close();
  process.exit(0);
});
