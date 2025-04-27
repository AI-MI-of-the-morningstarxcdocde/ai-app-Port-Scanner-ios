import SwiftUI
import LocalAuthentication
import Combine

@MainActor
class AppCoordinator: ObservableObject {
    static let shared = AppCoordinator()
    
    @Published var hasUnlockedFeatures: Bool = false
    @Published var isAuthenticated: Bool = false
    @Published var currentScanInProgress: Bool = false
    @Published var scanCount: Int = 0
    @Published var lastScanDate: Date?
    
    private let securityManager = SecurityManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        setupNotifications()
        loadStoredState()
    }
    
    private func setupNotifications() {
        NotificationCenter.default.publisher(for: .scanCompleted)
            .sink { [weak self] notification in
                self?.handleScanCompletion(notification)
            }
            .store(in: &cancellables)
        
        NotificationCenter.default.publisher(for: .aiScanCompleted)
            .sink { [weak self] _ in
                self?.handleAIScanCompletion()
            }
            .store(in: &cancellables)
        
        NotificationCenter.default.publisher(for: .wirelessAttackCompleted)
            .sink { [weak self] _ in
                self?.handleWirelessAttackCompletion()
            }
            .store(in: &cancellables)
    }
    
    private func loadStoredState() {
        // Load premium status
        if let data = try? securityManager.loadFromKeychain(key: "premium_status"),
           let status = String(data: data, encoding: .utf8) {
            hasUnlockedFeatures = status == "active"
        }
        
        // Load scan count
        if let data = try? securityManager.loadFromKeychain(key: "scan_count"),
           let count = Int(String(data: data, encoding: .utf8) ?? "0") {
            scanCount = count
        }
        
        // Load last scan date
        if let data = try? securityManager.loadFromKeychain(key: "last_scan_date"),
           let dateString = String(data: data, encoding: .utf8),
           let date = ISO8601DateFormatter().date(from: dateString) {
            lastScanDate = date
        }
    }
    
    func authenticate() async -> Bool {
        do {
            isAuthenticated = try await securityManager.authenticateUser()
            return isAuthenticated
        } catch {
            print("Authentication failed: \(error.localizedDescription)")
            isAuthenticated = false
            return false
        }
    }
    
    func startScan(target: String, ports: String) -> Bool {
        guard isAuthenticated else {
            Task {
                if await authenticate() {
                    currentScanInProgress = true
                    return true
                }
            }
            return false
        }
        
        currentScanInProgress = true
        return true
    }
    
    func endScan() {
        currentScanInProgress = false
    }
    
    private func handleScanCompletion(_ notification: Notification) {
        guard let scanResult = notification.object as? ScanResult else { return }
        
        scanCount += 1
        lastScanDate = Date()
        
        // Save updated state
        saveState()
        
        // Update achievements
        if scanCount == 1 {
            AchievementManager.shared.unlockAchievement(id: "first_scan")
        } else if scanCount == 10 {
            AchievementManager.shared.unlockAchievement(id: "power_user")
        }
        
        currentScanInProgress = false
    }
    
    private func handleAIScanCompletion() {
        AchievementManager.shared.unlockAchievement(id: "ai_master")
        currentScanInProgress = false
    }
    
    private func handleWirelessAttackCompletion() {
        AchievementManager.shared.unlockAchievement(id: "wireless_expert")
        currentScanInProgress = false
    }
    
    private func saveState() {
        // Save scan count
        if let data = String(scanCount).data(using: .utf8) {
            try? securityManager.saveToKeychain(key: "scan_count", data: data)
        }
        
        // Save last scan date
        if let data = ISO8601DateFormatter().string(from: lastScanDate ?? Date()).data(using: .utf8) {
            try? securityManager.saveToKeychain(key: "last_scan_date", data: data)
        }
    }
    
    func unlockPremiumFeatures() {
        hasUnlockedFeatures = true
        if let data = "active".data(using: .utf8) {
            try? securityManager.saveToKeychain(key: "premium_status", data: data)
        }
    }
    
    func lockPremiumFeatures() {
        hasUnlockedFeatures = false
        if let data = "inactive".data(using: .utf8) {
            try? securityManager.saveToKeychain(key: "premium_status", data: data)
        }
    }
}

extension Notification.Name {
    static let scanCompleted = Notification.Name("scanCompleted")
    static let aiScanCompleted = Notification.Name("aiScanCompleted")
    static let wirelessAttackCompleted = Notification.Name("wirelessAttackCompleted")
}