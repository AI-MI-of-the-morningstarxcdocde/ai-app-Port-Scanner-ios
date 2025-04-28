#!/usr/bin/env python3
"""
NX MCP Server Starter
This script starts the nx-mcp server on port 9686 for SSE connections
and can run it as a background daemon process
"""

import os
import sys
import subprocess
import time
import signal
import socket
import logging
import atexit
import json
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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(SCRIPT_DIR, "nx_mcp_server.pid")
NODE_PID_FILE = os.path.join(SCRIPT_DIR, "node_server.pid")
PORT = 9686

def check_port_available(port):
    """Check if a port is available to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_process_by_port(port):
    """Find process using the specified port."""
    try:
        cmd = f"lsof -i tcp:{port} -t"
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        if output:
            # Could be multiple PIDs, return the first one
            return int(output.split()[0])
        return None
    except subprocess.CalledProcessError:
        return None

def check_server_running():
    """Check if the server is already running by checking PID file and port."""
    # First check the PID file
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            # Check if process with this PID exists
            try:
                os.kill(pid, 0)
                return True, pid
            except OSError:
                # Process doesn't exist but PID file does, clean up
                os.remove(PID_FILE)
        except (ValueError, IOError):
            # Invalid PID file, remove it
            try:
                os.remove(PID_FILE)
            except OSError:
                pass
    
    # Also check if the Node.js server is running
    if os.path.exists(NODE_PID_FILE):
        try:
            with open(NODE_PID_FILE, 'r') as f:
                node_pid = int(f.read().strip())
            # Check if process exists
            try:
                os.kill(node_pid, 0)
                return True, node_pid
            except OSError:
                # Process doesn't exist but PID file does, clean up
                os.remove(NODE_PID_FILE)
        except (ValueError, IOError):
            try:
                os.remove(NODE_PID_FILE)
            except OSError:
                pass
    
    # Finally check if the port is in use
    pid = find_process_by_port(PORT)
    if pid:
        # Found a process using our port but no PID file, create one
        logging.info(f"Found a process (PID {pid}) using port {PORT} without PID file. Tracking it.")
        with open(NODE_PID_FILE, 'w') as f:
            f.write(str(pid))
        return True, pid
    
    return False, None

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
    os.chdir(SCRIPT_DIR)
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
    
    log_file = os.path.join(SCRIPT_DIR, "nx_mcp_server.log")
    with open(log_file, 'a+') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())
    
    # Write PID file
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    # Register a function to clean up PID file on exit
    atexit.register(lambda: os.path.exists(PID_FILE) and os.remove(PID_FILE))
    
    # Now we're a daemon!
    return os.getpid()

def kill_process(pid):
    """Kill a process with the given PID."""
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
                return True
        
        # Force kill if still running after 5 seconds
        os.kill(pid, signal.SIGKILL)
        time.sleep(0.5)
        try:
            os.kill(pid, 0)
            return False  # Process still exists somehow
        except OSError:
            return True  # Process is gone
    except OSError:
        # Process doesn't exist
        return True

def stop_server():
    """Stop the running server."""
    # Try to stop using PID file first
    stopped = False
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            if kill_process(pid):
                logging.info(f"Main server process (PID {pid}) stopped.")
                stopped = True
            
            # Remove PID file regardless
            os.remove(PID_FILE)
        except (ValueError, IOError) as e:
            logging.error(f"Error reading PID file: {e}")
    
    # Also stop the Node.js server
    node_stopped = False
    if os.path.exists(NODE_PID_FILE):
        try:
            with open(NODE_PID_FILE, 'r') as f:
                node_pid = int(f.read().strip())
            
            if kill_process(node_pid):
                logging.info(f"Node.js server (PID {node_pid}) stopped.")
                node_stopped = True
            
            # Remove PID file regardless
            os.remove(NODE_PID_FILE)
        except (ValueError, IOError) as e:
            logging.error(f"Error reading Node PID file: {e}")
    
    # Finally check if there's any process still using our port
    port_pid = find_process_by_port(PORT)
    if port_pid:
        logging.info(f"Found process (PID {port_pid}) still using port {PORT}, killing it.")
        if kill_process(port_pid):
            logging.info(f"Process using port {PORT} (PID {port_pid}) stopped.")
            stopped = True
    
    return stopped or node_stopped

def free_port_if_needed():
    """Ensure the port is free by killing any process using it."""
    if check_port_available(PORT):
        return True
    
    pid = find_process_by_port(PORT)
    if not pid:
        logging.error(f"Port {PORT} is in use but no process found using it.")
        return False
    
    logging.info(f"Process with PID {pid} is using port {PORT}, killing it.")
    if kill_process(pid):
        time.sleep(1)  # Give the port time to be freed
        return check_port_available(PORT)
    
    return False

def start_nx_server():
    """Start the nx-mcp server using Nx CLI and Node.js."""
    try:
        # Get the current directory where the script is located
        script_dir = Path(SCRIPT_DIR)
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
            text=True
        )
        
        # Check if daemon started successfully
        if process.returncode != 0:
            logging.error(f"Failed to start nx daemon. Exit code: {process.returncode}")
            logging.error(f"Output: {process.stdout}")
            logging.error(f"Error: {process.stderr}")
            return False
            
        logging.info("nx daemon started successfully")
        
        # Now start the Node.js server to serve SSE on port 9686
        sse_server_js = script_dir / "nx_mcp_server.js"
        
        # We already updated the SSE server JavaScript file, so no need to rewrite it
        
        # Get the full path to node executable
        try:
            node_path = subprocess.check_output(["which", "node"], text=True).strip()
        except subprocess.CalledProcessError:
            logging.error("Could not find Node.js executable. Make sure Node.js is installed.")
            return False
        
        # Start the SSE server using node
        logging.info(f"Starting SSE server with command: {node_path} {sse_server_js}")
        
        # Start SSE server process as detached and redirect output
        log_file = open(os.path.join(script_dir, "node_server.log"), "a")
        
        sse_process = subprocess.Popen(
            [node_path, str(sse_server_js)],
            cwd=script_dir,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            start_new_session=True  # Detach the process
        )
        
        # Write the process ID to a file for later management
        with open(NODE_PID_FILE, "w") as pid_file:
            pid_file.write(str(sse_process.pid))
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Check if the server is responsive
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:9686/health", timeout=3)
            if response.getcode() == 200:
                logging.info("SSE server health check passed")
            else:
                logging.warning(f"SSE server health check failed with status {response.getcode()}")
        except Exception as e:
            logging.warning(f"SSE server health check couldn't be completed: {e}")
            
            # Check if the process is still running
            if sse_process.poll() is not None:
                logging.error(f"SSE server process exited with code {sse_process.returncode}")
                return False
            
            logging.info("Continuing anyway as the process seems to have started")
        
        logging.info("nx-mcp SSE server started successfully on port 9686")
        return True
        
    except Exception as e:
        logging.error(f"Error starting nx-mcp server: {e}")
        return False

def save_server_status(status):
    """Save server status to a file for tracking."""
    status_file = os.path.join(SCRIPT_DIR, 'nx_mcp_status.json')
    status_data = {
        'timestamp': time.time(),
        'running': status[0],
        'pid': status[1] if status[0] else None,
        'port': PORT,
    }
    try:
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    except Exception as e:
        logging.warning(f"Failed to save server status: {e}")

def main():
    """Main function to start, stop, or check the server status."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            server_running, pid = check_server_running()
            if server_running:
                logging.info(f"Server is already running with PID {pid}.")
                save_server_status((True, pid))
                return
            
            if not free_port_if_needed():
                logging.error("Unable to free port 9686. Exiting.")
                sys.exit(1)
                
            pid = start_daemon()
            logging.info(f"Starting nx-mcp server in daemon mode with PID {pid}")
            success = start_nx_server()
            if success:
                logging.info("nx-mcp server started successfully in daemon mode")
                save_server_status((True, pid))
            else:
                logging.error("Failed to start nx-mcp server in daemon mode")
                save_server_status((False, None))
                sys.exit(1)
                
        elif command == "stop":
            if stop_server():
                logging.info("Server has been stopped successfully.")
                save_server_status((False, None))
            else:
                logging.warning("No server processes found to stop, but cleaned up any stale PID files.")
                save_server_status((False, None))
                
        elif command == "status":
            server_running, pid = check_server_running()
            if server_running:
                logging.info(f"Server is running with PID {pid}.")
                
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
            
            save_server_status((server_running, pid))
                
        elif command == "restart":
            logging.info("Restarting nx-mcp server...")
            stop_server()
            time.sleep(1)
            
            if not free_port_if_needed():
                logging.error("Unable to free port 9686 for restart. Exiting.")
                save_server_status((False, None))
                sys.exit(1)
                
            pid = start_daemon()
            logging.info(f"Starting nx-mcp server in daemon mode with PID {pid}")
            success = start_nx_server()
            if success:
                logging.info("nx-mcp server restarted successfully")
                save_server_status((True, pid))
            else:
                logging.error("Failed to restart nx-mcp server")
                save_server_status((False, None))
                sys.exit(1)
                
        elif command == "force-kill":
            # Special command to aggressively kill all related processes
            logging.info("Force killing all nx-mcp related processes")
            
            # Kill any process using our port
            port_pid = find_process_by_port(PORT)
            if port_pid:
                logging.info(f"Force killing process (PID {port_pid}) using port {PORT}")
                kill_process(port_pid)
            
            # Clean up PID files
            for pid_file in [PID_FILE, NODE_PID_FILE]:
                if os.path.exists(pid_file):
                    os.remove(pid_file)
            
            logging.info("All nx-mcp related processes should be terminated")
            save_server_status((False, None))
            
        else:
            logging.error(f"Unknown command: {command}")
            logging.info("Usage: python3 start_nx_mcp_server.py [start|stop|status|restart|force-kill]")
            sys.exit(1)
            
    else:
        # No command provided, run in foreground mode
        server_running, pid = check_server_running()
        if server_running:
            logging.info(f"Server is already running with PID {pid}.")
            logging.info("Use 'stop' command to stop it or 'restart' to restart it.")
            sys.exit(0)
            
        if not free_port_if_needed():
            logging.error("Unable to free port 9686. Exiting.")
            sys.exit(1)
            
        logging.info("Starting nx-mcp server in foreground mode")
        success = start_nx_server()
        
        if success:
            logging.info("nx-mcp server running at http://localhost:9686/sse")
            logging.info("Press Ctrl+C to stop the server")
            save_server_status((True, os.getpid()))
            
            # Keep the script running to maintain the server
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info("Shutting down nx-mcp server...")
                
                # Stop the Node.js server
                if os.path.exists(NODE_PID_FILE):
                    try:
                        with open(NODE_PID_FILE, 'r') as f:
                            node_pid = int(f.read().strip())
                        kill_process(node_pid)
                        logging.info(f"Node.js server (PID {node_pid}) has been stopped.")
                        os.remove(NODE_PID_FILE)
                    except (OSError, ValueError) as e:
                        logging.error(f"Error stopping Node.js server: {e}")
                
                save_server_status((False, None))
        else:
            logging.error("Failed to start nx-mcp server")
            save_server_status((False, None))
            sys.exit(1)

if __name__ == "__main__":
    main()