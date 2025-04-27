import SwiftUI

struct MainTabView: View {
    @EnvironmentObject private var themeManager: ThemeManager
    @EnvironmentObject private var appCoordinator: AppCoordinator
    @EnvironmentObject private var navigationCoordinator: NavigationCoordinator
    @State private var selectedTab = 0
    @State private var showSettings = false
    
    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationView {
                ContentView()
                    .navigationBarItems(trailing: settingsButton)
            }
            .tabItem {
                Label("Port Scan", systemImage: "antenna.radiowaves.left.and.right")
            }
            .tag(0)
            
            NavigationView {
                WirelessAttackView()
                    .navigationBarItems(trailing: settingsButton)
            }
            .tabItem {
                Label("Wireless", systemImage: "wifi.exclamationmark")
            }
            .tag(1)
            
            NavigationView {
                AIPredictiveScanView()
                    .navigationBarItems(trailing: settingsButton)
            }
            .tabItem {
                Label("AI Scan", systemImage: "brain.head.profile")
            }
            .tag(2)
            
            NavigationView {
                ChatbotView()
                    .navigationBarItems(trailing: settingsButton)
            }
            .tabItem {
                Label("Chatbot", systemImage: "message")
            }
            .tag(3)
            
            NavigationView {
                ARVisualizationContainerView()
                    .navigationBarItems(trailing: settingsButton)
            }
            .tabItem {
                Label("AR View", systemImage: "arkit")
            }
            .tag(4)
            
            NavigationView {
                AnalyticsDashboardView()
                    .navigationBarItems(trailing: settingsButton)
            }
            .tabItem {
                Label("Analytics", systemImage: "chart.bar.xaxis")
            }
            .tag(5)
        }
        .tint(themeManager.theme.accentColor.color)
        .sheet(isPresented: $showSettings) {
            NavigationView {
                SettingsView()
                    .navigationBarItems(
                        trailing: Button("Done") {
                            showSettings = false
                        }
                    )
            }
        }
    }
    
    private var settingsButton: some View {
        Button(action: { showSettings = true }) {
            Image(systemName: "gear")
        }
    }
}

struct SettingsView: View {
    @EnvironmentObject private var appCoordinator: AppCoordinator
    @EnvironmentObject private var themeManager: ThemeManager
    @State private var showBiometricAuth = false
    
    var body: some View {
        Form {
            Section(header: Text("Account")) {
                if appCoordinator.hasUnlockedFeatures {
                    Text("Premium Account")
                        .foregroundColor(.green)
                } else {
                    Button("Upgrade to Premium") {
                        NavigationCoordinator.shared.presentSheet(.monetization)
                    }
                }
            }
            
            Section(header: Text("Security")) {
                Toggle("Use Face ID / Touch ID", isOn: $showBiometricAuth)
                    .onChange(of: showBiometricAuth) { newValue in
                        if newValue {
                            Task {
                                await appCoordinator.authenticate()
                            }
                        }
                    }
            }
            
            Section(header: Text("Appearance")) {
                NavigationLink("Theme Settings") {
                    ThemeSettingsView()
                }
            }
            
            Section(header: Text("Achievements")) {
                NavigationLink("View Achievements") {
                    GamificationView()
                }
            }
            
            Section(header: Text("About")) {
                HStack {
                    Text("Version")
                    Spacer()
                    Text("1.0.0")
                        .foregroundColor(.secondary)
                }
                
                Link("Privacy Policy", destination: URL(string: "https://example.com/privacy")!)
                Link("Terms of Service", destination: URL(string: "https://example.com/terms")!)
            }
        }
        .navigationTitle("Settings")
    }
}

struct MainTabView_Previews: PreviewProvider {
    static var previews: some View {
        MainTabView()
            .environmentObject(ThemeManager())
            .environmentObject(AppCoordinator.shared)
            .environmentObject(NavigationCoordinator.shared)
    }
}
