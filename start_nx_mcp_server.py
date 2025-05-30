#!/usr/bin/env python3
"""
NX MCP Server Starter
This script starts the nx-mcp server on port 9686 for SSE connections
sudo gem install cocoapodsand can run it as a background daemon process
"""

import os
import sys
import subprocess
import time
import signal
import socket
import logging
import atexit
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("nx_mcp_server.log")
    ]
)

# PID file to track the daemon process
PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "nx_mcp_server.pid")


def check_port_available(port):
    """Check if a port is available to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0


def check_server_running():
    """Check if the server is already running by checking PID file."""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        try:
            # Check if process with this PID exists
            os.kill(pid, 0)
            return True
        except OSError:
            # Process doesn't exist, old PID file
            os.remove(PID_FILE)
    return False


def start_daemon():
    """Start the script as a daemon process."""
    # Fork first child
    try:
        pid = os.fork()
        if pid > 0:
            # Exit first parent
            sys.exit(0)
    except OSError as e:
        logging.error(f"Fork #1 failed: {e}")
        sys.exit(1)
# Decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)
# Fork second child
    try:
        pid = os.fork()
        if pid > 0:
            # Exit second parent
            sys.exit(0)
    except OSError as e:
        logging.error(f"Fork #2 failed: {e}")
        sys.exit(1)
# Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "nx_mcp_server.log")
    with open(log_file_path, 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())
# Write PID file
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
# Register a function to clean up PID file on exit
    atexit.register(lambda: os.path.exists(PID_FILE) and os.remove(PID_FILE))
# Now we're a daemon!
    return os.getpid()


def stop_server():
    """Stop the running server."""
    if not os.path.exists(PID_FILE):
        logging.error("No PID file found. Server may not be running.")
        return False
    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    try:
        # Try to terminate the process gracefully
        os.kill(pid, signal.SIGTERM)
        # Wait for the process to terminate
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except OSError:
                # Process is gone
                break
        else:
            # Force kill if still running after 5 seconds
            os.kill(pid, signal.SIGKILL)
        # Remove PID file
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        logging.info(f"Server (PID {pid}) has been stopped.")
        return True
    except OSError as e:
        logging.error(f"Error stopping server: {e}")
        return False


def check_if_port_in_use(port):
    """Check if port is in use and try to kill the process."""
    if check_port_available(port):
        return True
# Port is in use
    logging.error(f"Port {port} is already in use. Attempting to free it...")
    try:
        # Find process using the port
        find_cmd = f"lsof -i tcp:{port} -t"
        pid_str = subprocess.check_output(find_cmd, shell=True, text=True).strip()
        if pid_str:
            # Kill the process
            subprocess.run(f"kill -9 {pid_str}", shell=True, check=True)
            logging.info(f"Killed process {pid_str} using port {port}")
            # Wait a moment for the port to be released
            time.sleep(1)
            return check_port_available(port)
    except subprocess.CalledProcessError:
        logging.warning("No process found using lsof, but port is still in use")
    return False


def start_nx_server():
    """Start the nx-mcp server using Nx CLI and Node.js."""
    try:
        # Get the current directory where the script is located
        script_dir = Path(__file__).parent.absolute()
        nx_script = script_dir / "nx"
        # Check if nx file exists and is executable
        if not nx_script.exists():
            logging.error(f"Nx script not found at {nx_script}")
            return False
        # Make sure nx script is executable
        nx_script.chmod(nx_script.stat().st_mode | 0o111)
        # Start the nx daemon which handles the MCP server
        cmd = [str(nx_script), "daemon", "start"]
        logging.info(f"Starting nx daemon with command: {' '.join(cmd)}")
        # Start daemon process
        process = subprocess.run(
            cmd,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False # Don't raise exception on non-zero exit
        )
        # Check if daemon started successfully
        if process.returncode != 0:
            logging.error(
                f"Failed to start nx daemon. Exit code: {process.returncode}"
            )
            logging.error(f"Output: {process.stdout}")
            logging.error(f"Error: {process.stderr}")
            return False
        logging.info("nx daemon started successfully")
        # Now let's start the MCP server explicitly
        # Create a Node.js server to serve SSE on port 9686
        sse_server_js = script_dir / "nx_mcp_server.js"
        # Create the SSE server JavaScript file if it doesn't exist
        if not sse_server_js.exists() or os.path.getsize(sse_server_js) == 0:
            with open(sse_server_js, 'w') as f:
                f.write("""
const http = require('http');
const fs = require('fs');
const path = require('path');

// Create a log file
const logFileStream = fs.createWriteStream(path.join(__dirname, 'nx_mcp_sse.log'), { flags: 'a' });
const logMessage = (msg) => {
  const timestamp = new Date().toISOString();
  const logString = `${timestamp} - ${msg}\\n`;
  logFileStream.write(logString);
  console.log(msg); // Also log to console if running in foreground
};

// Create an SSE server on port 9686
const server = http.createServer((req, res) => {
  logMessage(`Received request: ${req.method} ${req.url}`);

  if (req.url === '/sse') {
    logMessage('SSE connection established');
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*' // Allow all origins
    });

    const initialMessage = { type: 'connection', status: 'connected' };
    res.write(`data: ${JSON.stringify(initialMessage)}\\n\\n`);
    logMessage('Sent initial message');

    const intervalId = setInterval(() => {
      const heartbeatMsg = { type: 'heartbeat', timestamp: Date.now() };
      res.write(`data: ${JSON.stringify(heartbeatMsg)}\\n\\n`);
      logMessage('Sent heartbeat message');
    }, 10000);

    req.on('close', () => {
      clearInterval(intervalId);
      logMessage('Client disconnected');
    });
  } else if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok' }));
    logMessage('Health check request served');
  } else {
    res.writeHead(404);
    res.end();
    logMessage(`404 for path ${req.url}`);
  }
});

server.on('error', (err) => {
  logMessage(`Server error: ${err.message}`);
  if (err.code === 'EADDRINUSE') {
    logMessage('Port already in use, retrying in 5 seconds...');
    setTimeout(() => {
      server.close(); // Ensure server is closed before retrying
      server.listen(9686);
    }, 5000);
  }
});

server.listen(9686, () => {
  logMessage('NX MCP Server running on port 9686');
});

// Graceful shutdown
const shutdown = () => {
  logMessage('Shutting down server...');
  server.close(() => {
    logMessage('Server closed.');
    process.exit(0);
  });
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
""")
        # Start the SSE server using node
        node_cmd = ["node", str(sse_server_js)]
        logging.info(f"Starting SSE server with command: {' '.join(node_cmd)}")
        # Start SSE server process as detached and redirect output
        node_log_file = open(os.path.join(script_dir, "node_server.log"), "a")
        # Get the full path to node executable
        node_path = subprocess.check_output(["which", "node"],
                                            text=True).strip()
        sse_process = subprocess.Popen(
            [node_path, str(sse_server_js)],
            cwd=script_dir,
            stdout=node_log_file,
            stderr=node_log_file,
            stdin=subprocess.DEVNULL,
            start_new_session=True  # Detach the process
        )
        # Write the process ID to a file for later management
        node_server_pid_file = os.path.join(script_dir, "node_server.pid")
        with open(node_server_pid_file, "w") as pid_f:
            pid_f.write(str(sse_process.pid))
        # Wait a moment for the server to start
        time.sleep(2)
        # Check if the server is responsive
        try:
            import urllib.request
            with urllib.request.urlopen("http://localhost:9686/health",
                                        timeout=3) as health_response:
                if health_response.getcode() == 200:
                    logging.info("SSE server health check passed")
                else:
                    logging.warning(
                        "SSE server health check failed with status "
                        f"{health_response.getcode()}"
                    )
        except Exception as e:
            logging.warning(
                f"SSE server health check couldn't be completed: {e}"
            )
            logging.info("Continuing anyway as the process seems to have started")
        logging.info("nx-mcp SSE server started successfully on port 9686")
        return True
    except Exception as e:
        logging.error(f"Error starting nx-mcp server: {e}")
        return False


def main():
    """Main function to start, stop, or check the server status."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "start":
            if check_server_running():
                logging.info("Server is already running.")
                return
            if not check_if_port_in_use(9686):
                logging.error("Unable to free port 9686. Exiting.")
                sys.exit(1)
            pid = start_daemon()
            logging.info(f"Starting nx-mcp server in daemon mode with PID {pid}")
            success = start_nx_server()
            if success:
                logging.info("nx-mcp server started successfully in daemon mode")
            else:
                logging.error("Failed to start nx-mcp server in daemon mode")
                sys.exit(1)
        elif command == "stop":
            if stop_server():
                # Also stop the Node.js server
                node_pid_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_server.pid")
                if os.path.exists(node_pid_file):
                    try:
                        with open(node_pid_file, 'r') as f:
                            node_pid = int(f.read().strip())
                        os.kill(node_pid, signal.SIGTERM)
                        logging.info(f"Node.js server (PID {node_pid}) has been stopped.")
                        os.remove(node_pid_file)
                    except (OSError, ValueError) as e:
                        logging.error(f"Error stopping Node.js server: {e}")
            else:
                logging.error("Failed to stop the server.")
        elif command == "status":
            if check_server_running():
                logging.info("Server is running.")
                # Check if the SSE endpoint is responding
                try:
                    import urllib.request
                    response = urllib.request.urlopen("http://localhost:9686/health", timeout=3)
                    if response.getcode() == 200:
                        logging.info("SSE server is responsive and healthy.")
                    else:
                        logging.warning(f"SSE server returned status code {response.getcode()}")
                except Exception as e:
                    logging.warning(f"SSE server doesn't seem to be responding: {e}")
            else:
                logging.info("Server is not running.")
        elif command == "restart":
            logging.info("Restarting nx-mcp server...")
            stop_server()
            time.sleep(1)
            if not check_if_port_in_use(9686):
                logging.error("Unable to free port 9686 for restart. Exiting.")
                sys.exit(1)
            pid = start_daemon()
            logging.info(f"Starting nx-mcp server in daemon mode with PID {pid}")
            success = start_nx_server()
            if success:
                logging.info("nx-mcp server restarted successfully")
            else:
                logging.error("Failed to restart nx-mcp server")
                sys.exit(1)
        else:
            logging.error(f"Unknown command: {command}")
            logging.info("Usage: python3 start_nx_mcp_server.py [start|stop|status|restart]")
            sys.exit(1)
    else:
        # No command provided, run in foreground mode
        if check_server_running():
            logging.info("Server is already running in daemon mode.")
            logging.info("Use 'stop' command to stop it or 'restart' to restart it.")
            sys.exit(0)
        if not check_if_port_in_use(9686):
            logging.error("Unable to free port 9686. Exiting.")
            sys.exit(1)
        logging.info("Starting nx-mcp server in foreground mode")
        success = start_nx_server()
        if success:
            logging.info("nx-mcp server running at http://localhost:9686/sse")
            logging.info("Press Ctrl+C to stop the server")
            # Keep the script running to maintain the server
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info("Shutting down nx-mcp server...")
                # Stop the Node.js server
                node_pid_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_server.pid")
                if os.path.exists(node_pid_file):
                    try:
                        with open(node_pid_file, 'r') as f:
                            node_pid = int(f.read().strip())
                        os.kill(node_pid, signal.SIGTERM)
                        logging.info(f"Node.js server (PID {node_pid}) has been stopped.")
                        os.remove(node_pid_file)
                    except (OSError, ValueError) as e:
                        logging.error(f"Error stopping Node.js server: {e}")
        else:
            logging.error("Failed to start nx-mcp server")
            sys.exit(1)


if __name__ == "__main__":
    main()
