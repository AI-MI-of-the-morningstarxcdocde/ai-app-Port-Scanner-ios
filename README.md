# ai-app-Port-Scanner-ios

## Overview
The ai-app-Port-Scanner-ios is a comprehensive network security tool designed for professionals and enthusiasts. It combines powerful scanning capabilities with advanced features like AI-driven predictions, blockchain logging, and real-time threat intelligence.

## Features
- Multi-threaded port scanning
- IPv6 support
- AI-predicted open ports
- SSL/TLS certificate validation
- Honeypot simulation
- Network traffic analysis
- RESTful API for third-party integration
- iOS app with AR visualization and voice commands

## Installation

### Python Backend
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/port-scanner.git
   cd port-scanner
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend server:
   ```bash
   python api_server.py
   ```

### iOS App
1. Open `AdvancedPortScanner.xcodeproj` in Xcode.
2. Configure your development team in the project settings.
3. Build and run the app on a simulator or device.

## Usage

### Python Backend
- Start a port scan:
  ```bash
  python scanner/port_scanner.py --target 127.0.0.1 --ports 22,80
  ```
- Validate an SSL certificate:
  ```bash
  python scanner/port_scanner.py --validate-ssl example.com
  ```

### RESTful API
- Start the API server:
  ```bash
  python api_server.py
  ```
- Example API request:
  ```bash
  curl -X POST http://localhost:5000/api/v1/scan \
       -H "X-API-Key: YOUR_API_KEY" \
       -H "Content-Type: application/json" \
       -d '{"target": "127.0.0.1", "ports": "22,80"}'
  ```

## RESTful API Documentation

### Endpoints

#### 1. Start a Port Scan
- **URL**: `/api/v1/scan`
- **Method**: `POST`
- **Headers**:
  - `X-API-Key`: Your API key
- **Body**:
  ```json
  {
    "target": "127.0.0.1",
    "ports": "22,80"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Scan started successfully",
    "scan_id": "123456"
  }
  ```

#### 2. Get Scan Results
- **URL**: `/api/v1/scan/<scan_id>`
- **Method**: `GET`
- **Headers**:
  - `X-API-Key`: Your API key
- **Response**:
  ```json
  {
    "results": [
      {"port": 22, "status": "open", "service": "SSH"},
      {"port": 80, "status": "open", "service": "HTTP"}
    ]
  }
  ```

#### 3. Validate SSL Certificate
- **URL**: `/api/v1/certificate`
- **Method**: `POST`
- **Headers**:
  - `X-API-Key`: Your API key
- **Body**:
  ```json
  {
    "hostname": "example.com"
  }
  ```
- **Response**:
  ```json
  {
    "hostname": "example.com",
    "valid": true,
    "daysToExpiration": 90
  }
  ```

## License
This project is licensed under the MIT License. See the LICENSE file for details.
