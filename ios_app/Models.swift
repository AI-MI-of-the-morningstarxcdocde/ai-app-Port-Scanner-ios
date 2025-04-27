import Foundation

// MARK: - Scan Models

struct ScanResult: Codable {
    let target: String
    let ports: String
    let results: [String]
    let timestamp: Date
    let scanDuration: TimeInterval
    
    enum CodingKeys: String, CodingKey {
        case target, ports, results
        case timestamp = "scan_timestamp"
        case scanDuration = "duration"
    }
}

struct PredictiveScanResult: Codable {
    let target: String
    let predicted_open_ports: [Int]
    let confidence_scores: [Double]
    let reasoning: String
}

struct WirelessAttackResult: Codable {
    let target: String
    let status: String
    let vulnerabilities: [String]
    let recommendations: [String]
    let riskLevel: Int
    
    enum CodingKeys: String, CodingKey {
        case target, status, vulnerabilities, recommendations
        case riskLevel = "risk_level"
    }
}

// MARK: - Analytics Models

struct AnalyticsData: Codable {
    let currentMetrics: ScanMetrics
    let dailyMetrics: [DailyMetrics]
}

struct ScanMetrics: Codable {
    let totalScans: Int
    let openPorts: Int
    let vulnerabilities: Int
    let timeSpent: TimeInterval
    
    enum CodingKeys: String, CodingKey {
        case totalScans = "total_scans"
        case openPorts = "open_ports"
        case vulnerabilities
        case timeSpent = "time_spent"
    }
}

struct DailyMetrics: Identifiable, Codable {
    let id: UUID
    let date: Date
    let scans: Int
    let discoveries: Int
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(UUID.self, forKey: .id)
        date = try container.decode(Date.self, forKey: .date)
        scans = try container.decode(Int.self, forKey: .scans)
        discoveries = try container.decode(Int.self, forKey: .discoveries)
    }
}

// MARK: - Chat Models

struct ChatMessage: Identifiable, Equatable, Codable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date
    
    static func == (lhs: ChatMessage, rhs: ChatMessage) -> Bool {
        lhs.id == rhs.id
    }
}

struct ChatResponse: Codable {
    let message: String
    let response: String
    let suggestions: [String]
}

// MARK: - Network Models

struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let error: APIError?
}

struct APIError: Codable {
    let code: String
    let message: String
    let details: String?
}

// MARK: - Subscription Models

struct SubscriptionPlan: Identifiable, Codable {
    let id: String
    let name: String
    let description: String
    let price: Decimal
    let features: [String]
    let duration: Int // in days
}

struct PurchaseResult: Codable {
    let transactionId: String
    let purchaseDate: Date
    let productId: String
    let isActive: Bool
}