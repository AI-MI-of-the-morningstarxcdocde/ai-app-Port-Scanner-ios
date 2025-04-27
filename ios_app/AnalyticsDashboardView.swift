import SwiftUI
import Combine

struct AnalyticsDashboardView: View {
    @StateObject private var coordinator = AppCoordinator.shared
    @State private var analyticsData: AnalyticsData?
    @State private var isLoading: Bool = false
    @State private var showAlert: Bool = false
    @State private var alertMessage: String = ""
    
    private var networkManager = NetworkManager.shared
    private var cancellables = Set<AnyCancellable>()
    
    var body: some View {
        ScrollView {
            if isLoading {
                ProgressView("Loading analytics...")
                    .padding()
            } else if !coordinator.hasUnlockedFeatures {
                premiumFeaturePrompt
            } else if let data = analyticsData {
                VStack(spacing: 20) {
                    metricsGrid(data.currentMetrics)
                    activityChart(data.dailyMetrics)
                    scanBreakdown(data.dailyMetrics)
                }
                .padding()
            } else {
                Text("No analytics data available")
                    .foregroundColor(.secondary)
                    .padding()
            }
        }
        .navigationTitle("Analytics")
        .alert(isPresented: $showAlert) {
            Alert(title: Text("Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
        }
        .onAppear {
            if coordinator.hasUnlockedFeatures {
                fetchAnalytics()
            }
        }
    }
    
    private var premiumFeaturePrompt: some View {
        VStack(spacing: 16) {
            Image(systemName: "chart.bar.xaxis")
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 60, height: 60)
                .foregroundColor(.blue)
            
            Text("Premium Analytics")
                .font(.title)
                .bold()
            
            Text("Unlock detailed analytics and insights by upgrading to Premium")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
            
            Button(action: {
                // Navigate to monetization view
            }) {
                Text("Upgrade to Premium")
                    .bold()
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            .padding(.horizontal)
        }
        .padding()
    }
    
    private func metricsGrid(_ metrics: ScanMetrics) -> some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
            MetricCard(
                title: "Total Scans",
                value: "\(metrics.totalScans)",
                icon: "chart.bar.fill",
                color: .blue
            )
            
            MetricCard(
                title: "Open Ports",
                value: "\(metrics.openPorts)",
                icon: "network",
                color: .green
            )
            
            MetricCard(
                title: "Vulnerabilities",
                value: "\(metrics.vulnerabilities)",
                icon: "exclamationmark.shield.fill",
                color: .red
            )
            
            MetricCard(
                title: "Time Spent",
                value: timeSpentFormatted(metrics.timeSpent),
                icon: "clock.fill",
                color: .orange
            )
        }
    }
    
    private func activityChart(_ metrics: [DailyMetrics]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Weekly Activity")
                .font(.headline)
            
            Chart(data: metrics.map { $0.scans })
                .frame(height: 200)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(15)
    }
    
    private func scanBreakdown(_ metrics: [DailyMetrics]) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Activity")
                .font(.headline)
            
            ForEach(metrics) { metric in
                HStack {
                    Text(formatDate(metric.date))
                    Spacer()
                    Text("\(metric.scans) scans")
                    Text("\(metric.discoveries) found")
                        .foregroundColor(.secondary)
                }
                .padding(.vertical, 8)
                
                if metric.id != metrics.last?.id {
                    Divider()
                }
            }
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(15)
    }
    
    private func fetchAnalytics() {
        isLoading = true
        
        networkManager.fetchAnalytics()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { completion in
                    isLoading = false
                    if case .failure(let error) = completion {
                        alertMessage = error.localizedDescription
                        showAlert = true
                    }
                },
                receiveValue: { data in
                    analyticsData = data
                }
            )
            .store(in: &cancellables)
    }
    
    private func timeSpentFormatted(_ timeSpent: TimeInterval) -> String {
        let hours = Int(timeSpent / 3600)
        return "\(hours)h"
    }
    
    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d"
        return formatter.string(from: date)
    }
}

struct Chart: View {
    let data: [Int]
    
    var body: some View {
        GeometryReader { geometry in
            HStack(alignment: .bottom, spacing: 8) {
                ForEach(data.indices, id: \.self) { index in
                    VStack {
                        Rectangle()
                            .fill(Color.blue)
                            .frame(width: barWidth(for: geometry.size.width),
                                   height: barHeight(for: geometry.size.height, value: data[index]))
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .bottom)
        }
    }
    
    private func barWidth(for totalWidth: CGFloat) -> CGFloat {
        let spacing: CGFloat = 8
        return (totalWidth - (spacing * CGFloat(data.count - 1))) / CGFloat(data.count)
    }
    
    private func barHeight(for totalHeight: CGFloat, value: Int) -> CGFloat {
        let maxValue = data.max() ?? 1
        return totalHeight * CGFloat(value) / CGFloat(maxValue)
    }
}

struct MetricCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: 30, height: 30)
                .foregroundColor(color)
            
            Text(value)
                .font(.title2)
                .bold()
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(15)
    }
}

struct AnalyticsDashboardView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {
            AnalyticsDashboardView()
        }
    }
}
