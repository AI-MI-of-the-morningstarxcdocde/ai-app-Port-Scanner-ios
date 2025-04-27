import SwiftUI

@main
struct AdvancedPortScannerApp: App {
    @StateObject private var appCoordinator = AppCoordinator.shared
    @StateObject private var navigationCoordinator = NavigationCoordinator.shared
    @StateObject private var themeManager = ThemeManager()
    
    var body: some Scene {
        WindowGroup {
            NavigationContainer {
                MainTabView()
                    .onAppear {
                        Task {
                            await appCoordinator.authenticate()
                        }
                    }
            }
            .environmentObject(appCoordinator)
            .environmentObject(navigationCoordinator)
            .environmentObject(themeManager)
        }
    }
}
