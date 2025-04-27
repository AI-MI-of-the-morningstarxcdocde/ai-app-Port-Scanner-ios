import Foundation
import Combine

enum NetworkError: Error {
    case invalidURL
    case requestFailed(Error)
    case invalidResponse
    case decodingFailed(Error)
    case unauthorized
    case noData
    
    var localizedDescription: String {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .requestFailed(let error):
            return "Request failed: \(error.localizedDescription)"
        case .invalidResponse:
            return "Invalid server response"
        case .decodingFailed(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .unauthorized:
            return "Unauthorized access"
        case .noData:
            return "No data received"
        }
    }
}

class NetworkManager {
    static let shared = NetworkManager()
    private let securityManager = SecurityManager.shared
    private let baseURL = "http://localhost:8000"
    
    private init() {}
    
    func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        body: Data? = nil,
        requiresAuth: Bool = true
    ) -> AnyPublisher<T, NetworkError> {
        guard let url = URL(string: "\(baseURL)/\(endpoint)") else {
            return Fail(error: NetworkError.invalidURL).eraseToAnyPublisher()
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.httpBody = body
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Apply security enhancements
        request = securityManager.secureRequest(request)
        
        return URLSession.shared.dataTaskPublisher(for: request)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw NetworkError.invalidResponse
                }
                
                switch httpResponse.statusCode {
                case 200...299:
                    return data
                case 401:
                    throw NetworkError.unauthorized
                default:
                    throw NetworkError.invalidResponse
                }
            }
            .decode(type: T.self, decoder: JSONDecoder())
            .mapError { error in
                if let networkError = error as? NetworkError {
                    return networkError
                }
                if error is DecodingError {
                    return NetworkError.decodingFailed(error)
                }
                return NetworkError.requestFailed(error)
            }
            .eraseToAnyPublisher()
    }
    
    // MARK: - Scanning Endpoints
    
    func performPortScan(target: String, ports: String) -> AnyPublisher<ScanResult, NetworkError> {
        let parameters = [
            "target": target,
            "ports": ports,
            "scan_type": "all"
        ]
        
        guard let jsonData = try? JSONEncoder().encode(parameters) else {
            return Fail(error: NetworkError.invalidResponse).eraseToAnyPublisher()
        }
        
        return request(
            endpoint: "scan/port",
            method: "POST",
            body: jsonData
        )
    }
    
    func performAIPredictiveScan(target: String) -> AnyPublisher<PredictiveScanResult, NetworkError> {
        let parameters = ["target": target]
        
        guard let jsonData = try? JSONEncoder().encode(parameters) else {
            return Fail(error: NetworkError.invalidResponse).eraseToAnyPublisher()
        }
        
        return request(
            endpoint: "scan/predictive",
            method: "POST",
            body: jsonData
        )
    }
    
    func performWirelessAttack(target: String) -> AnyPublisher<WirelessAttackResult, NetworkError> {
        let parameters = ["target": target]
        
        guard let jsonData = try? JSONEncoder().encode(parameters) else {
            return Fail(error: NetworkError.invalidResponse).eraseToAnyPublisher()
        }
        
        return request(
            endpoint: "attack/wireless",
            method: "POST",
            body: jsonData
        )
    }
    
    func sendChatMessage(_ message: String) -> AnyPublisher<ChatResponse, NetworkError> {
        let parameters = ["message": message]
        
        guard let jsonData = try? JSONEncoder().encode(parameters) else {
            return Fail(error: NetworkError.invalidResponse).eraseToAnyPublisher()
        }
        
        return request(
            endpoint: "chatbot",
            method: "POST",
            body: jsonData
        )
    }
    
    func fetchAnalytics() -> AnyPublisher<AnalyticsData, NetworkError> {
        request(endpoint: "analytics")
    }
}

// MARK: - Response Types

struct WirelessAttackResult: Codable {
    let target: String
    let status: String
}

struct AnalyticsData: Codable {
    let currentMetrics: ScanMetrics
    let dailyMetrics: [DailyMetrics]
}