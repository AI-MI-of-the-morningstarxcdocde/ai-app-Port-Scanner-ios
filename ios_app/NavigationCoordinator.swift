import SwiftUI

enum NavigationDestination: Hashable {
    case monetization
    case analytics
    case aiScan
    case wirelessAttack
    case arVisualization
    case chatbot
}

class NavigationCoordinator: ObservableObject {
    static let shared = NavigationCoordinator()
    
    @Published var navigationPath = NavigationPath()
    @Published var activeSheet: NavigationDestination?
    
    private init() {}
    
    func navigateTo(_ destination: NavigationDestination) {
        navigationPath.append(destination)
    }
    
    func presentSheet(_ destination: NavigationDestination) {
        activeSheet = destination
    }
    
    func dismissSheet() {
        activeSheet = nil
    }
    
    func navigateBack() {
        if !navigationPath.isEmpty {
            navigationPath.removeLast()
        }
    }
    
    func clearNavigation() {
        navigationPath = NavigationPath()
    }
}

struct NavigationContainer<Content: View>: View {
    @StateObject private var coordinator = NavigationCoordinator.shared
    @ViewBuilder let content: Content
    
    var body: some View {
        NavigationStack(path: $coordinator.navigationPath) {
            content
                .navigationDestination(for: NavigationDestination.self) { destination in
                    switch destination {
                    case .monetization:
                        MonetizationView()
                    case .analytics:
                        AnalyticsDashboardView()
                    case .aiScan:
                        AIPredictiveScanView()
                    case .wirelessAttack:
                        WirelessAttackView()
                    case .arVisualization:
                        ARVisualizationContainerView()
                    case .chatbot:
                        ChatbotView()
                    }
                }
                .sheet(item: $coordinator.activeSheet) { destination in
                    NavigationView {
                        switch destination {
                        case .monetization:
                            MonetizationView()
                        case .analytics:
                            AnalyticsDashboardView()
                        case .aiScan:
                            AIPredictiveScanView()
                        case .wirelessAttack:
                            WirelessAttackView()
                        case .arVisualization:
                            ARVisualizationContainerView()
                        case .chatbot:
                            ChatbotView()
                        }
                    }
                }
        }
    }
}