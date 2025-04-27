import SwiftUI
import Combine

class FeatureCoordinator: ObservableObject {
    static let shared = FeatureCoordinator()
    
    @Published var activePremiumFeatures: Set<PremiumFeature> = []
    @Published var scanInProgress = false
    @Published var lastScanResult: ScanResult?
    @Published var predictiveScanResult: PredictiveScanResult?
    @Published var wirelessAttackResult: WirelessAttackResult?
    
    private let achievementManager = AchievementManager.shared
    private let securityManager = SecurityManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    enum PremiumFeature: String {
        case aiPrediction
        case arVisualization
        case wirelessAttacks
        case detailedAnalytics
        case chatbot
    }
    
    private init() {
        setupFeatureObservers()
    }
    
    private func setupFeatureObservers() {
        // Monitor scan completions
        NotificationCenter.default.publisher(for: .scanCompleted)
            .sink { [weak self] notification in
                if let result = notification.object as? ScanResult {
                    self?.handleScanCompletion(result)
                }
            }
            .store(in: &cancellables)
        
        // Monitor AI predictions
        NotificationCenter.default.publisher(for: .aiPredictionCompleted)
            .sink { [weak self] notification in
                if let result = notification.object as? PredictiveScanResult {
                    self?.handleAIPrediction(result)
                }
            }
            .store(in: &cancellables)
        
        // Monitor wireless attacks
        NotificationCenter.default.publisher(for: .wirelessAttackCompleted)
            .sink { [weak self] notification in
                if let result = notification.object as? WirelessAttackResult {
                    self?.handleWirelessAttack(result)
                }
            }
            .store(in: &cancellables)
    }
    
    func startScan(target: String, ports: String) async throws {
        guard !scanInProgress else { return }
        
        scanInProgress = true
        defer { scanInProgress = false }
        
        // Authenticate before scanning
        guard try await securityManager.authenticateUser() else {
            throw SecurityError.authenticationFailed
        }
        
        // Check if AI prediction is available
        if activePremiumFeatures.contains(.aiPrediction) {
            try await performAIPredictiveScan(target: target)
        }
        
        // Perform the actual scan
        try await performPortScan(target: target, ports: ports)
        
        // If wireless attacks are available, perform additional checks
        if activePremiumFeatures.contains(.wirelessAttacks) {
            try await performWirelessScan(target: target)
        }
    }
    
    private func performPortScan(target: String, ports: String) async throws {
        // Simulated scan for demonstration
        try await Task.sleep(nanoseconds: 2 * 1_000_000_000)
        
        let result = ScanResult(
            target: target,
            ports: ports,
            results: ["Port 80: Open", "Port 443: Open"],
            timestamp: Date(),
            scanDuration: 2.0
        )
        
        await MainActor.run {
            self.lastScanResult = result
            NotificationCenter.default.post(name: .scanCompleted, object: result)
        }
    }
    
    private func performAIPredictiveScan(target: String) async throws {
        // Simulated AI prediction
        try await Task.sleep(nanoseconds: 1 * 1_000_000_000)
        
        let result = PredictiveScanResult(
            target: target,
            predicted_open_ports: [80, 443, 22],
            confidence_scores: [0.95, 0.92, 0.85],
            reasoning: "Historical data suggests these ports are commonly open on similar targets"
        )
        
        await MainActor.run {
            self.predictiveScanResult = result
            NotificationCenter.default.post(name: .aiPredictionCompleted, object: result)
        }
    }
    
    private func performWirelessScan(target: String) async throws {
        // Simulated wireless scan
        try await Task.sleep(nanoseconds: 1 * 1_000_000_000)
        
        let result = WirelessAttackResult(
            target: target,
            status: "Vulnerable",
            vulnerabilities: ["Weak WPA2 Password", "WPS Enabled"],
            recommendations: ["Disable WPS", "Use stronger password"],
            riskLevel: 3
        )
        
        await MainActor.run {
            self.wirelessAttackResult = result
            NotificationCenter.default.post(name: .wirelessAttackCompleted, object: result)
        }
    }
    
    private func handleScanCompletion(_ result: ScanResult) {
        achievementManager.unlockAchievement(id: "first_scan")
        
        if result.results.count > 5 {
            achievementManager.unlockAchievement(id: "power_user")
        }
    }
    
    private func handleAIPrediction(_ result: PredictiveScanResult) {
        achievementManager.unlockAchievement(id: "ai_master")
    }
    
    private func handleWirelessAttack(_ result: WirelessAttackResult) {
        achievementManager.unlockAchievement(id: "wireless_expert")
    }
    
    func activateFeature(_ feature: PremiumFeature) {
        activePremiumFeatures.insert(feature)
    }
    
    func deactivateFeature(_ feature: PremiumFeature) {
        activePremiumFeatures.remove(feature)
    }
}

// MARK: - Notifications
extension Notification.Name {
    static let scanCompleted = Notification.Name("scanCompleted")
    static let aiPredictionCompleted = Notification.Name("aiPredictionCompleted")
    static let wirelessAttackCompleted = Notification.Name("wirelessAttackCompleted")
}

// MARK: - SwiftUI Views

struct FeatureControlPanel: View {
    @ObservedObject private var coordinator = FeatureCoordinator.shared
    @State private var target = ""
    @State private var ports = ""
    @State private var showingError = false
    @State private var error: Error?
    
    var body: some View {
        VStack(spacing: 20) {
            TextField(NSLocalizedString("enter_target", comment: ""), text: $target)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            TextField(NSLocalizedString("enter_ports", comment: ""), text: $ports)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            Button(action: startScan) {
                if coordinator.scanInProgress {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle())
                } else {
                    Text(NSLocalizedString("start_scan", comment: ""))
                        .bold()
                        .frame(maxWidth: .infinity)
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(coordinator.scanInProgress)
            
            if let result = coordinator.lastScanResult {
                ScanResultView(result: result)
            }
            
            if let prediction = coordinator.predictiveScanResult {
                PredictionResultView(result: prediction)
            }
            
            if let wirelessResult = coordinator.wirelessAttackResult {
                WirelessResultView(result: wirelessResult)
            }
        }
        .padding()
        .alert(isPresented: $showingError) {
            Alert(
                title: Text(NSLocalizedString("error", comment: "")),
                message: Text(error?.localizedDescription ?? NSLocalizedString("unknown_error", comment: "")),
                dismissButton: .default(Text(NSLocalizedString("ok", comment: "")))
            )
        }
    }
    
    private func startScan() {
        Task {
            do {
                try await coordinator.startScan(target: target, ports: ports)
            } catch {
                await MainActor.run {
                    self.error = error
                    self.showingError = true
                }
            }
        }
    }
}

struct ScanResultView: View {
    let result: ScanResult
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(NSLocalizedString("scan_results", comment: ""))
                .font(.headline)
            
            ForEach(result.results, id: \.self) { item in
                Text(item)
                    .foregroundColor(.secondary)
            }
            
            Text("Duration: \(String(format: "%.2f", result.scanDuration))s")
                .font(.caption)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(10)
    }
}

struct PredictionResultView: View {
    let result: PredictiveScanResult
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("AI Prediction")
                .font(.headline)
            
            Text("Predicted Open Ports:")
            ForEach(Array(zip(result.predicted_open_ports, result.confidence_scores)), id: \.0) { port, confidence in
                HStack {
                    Text("Port \(port)")
                    Spacer()
                    Text("\(Int(confidence * 100))% confidence")
                        .foregroundColor(.secondary)
                }
            }
            
            Text(result.reasoning)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(10)
    }
}

struct WirelessResultView: View {
    let result: WirelessAttackResult
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Wireless Scan")
                .font(.headline)
            
            Text("Status: \(result.status)")
                .foregroundColor(result.status == "Vulnerable" ? .red : .green)
            
            if !result.vulnerabilities.isEmpty {
                Text("Vulnerabilities:")
                ForEach(result.vulnerabilities, id: \.self) { vulnerability in
                    Text("• \(vulnerability)")
                        .foregroundColor(.red)
                }
            }
            
            if !result.recommendations.isEmpty {
                Text("Recommendations:")
                ForEach(result.recommendations, id: \.self) { recommendation in
                    Text("• \(recommendation)")
                        .foregroundColor(.blue)
                }
            }
            
            Text("Risk Level: \(result.riskLevel)")
                .foregroundColor(riskLevelColor)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(10)
    }
    
    private var riskLevelColor: Color {
        switch result.riskLevel {
        case 1: return .green
        case 2: return .yellow
        case 3: return .red
        default: return .gray
        }
    }
}
