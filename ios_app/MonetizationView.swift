import SwiftUI
import StoreKit

struct PremiumFeature: Identifiable {
    let id = UUID()
    let name: String
    let description: String
    let icon: String
    let featureType: FeatureType
}

enum FeatureType {
    case wirelessAttacks
    case aiPrediction
    case arVisualization
    case advancedReports
}

struct Subscription: Identifiable {
    let id = UUID()
    let name: String
    let price: Decimal
    let period: String
    let features: [FeatureType]
    let productId: String
}

class MonetizationViewModel: ObservableObject {
    @Published var subscriptions: [Subscription] = []
    @Published var features: [PremiumFeature] = []
    @Published var selectedSubscription: Subscription?
    @Published var isPurchasing = false
    @Published var showingError = false
    @Published var errorMessage = ""
    
    init() {
        setupFeatures()
        setupSubscriptions()
    }
    
    private func setupFeatures() {
        features = [
            PremiumFeature(
                name: "Wireless Attack Detection",
                description: "Scan and identify vulnerabilities in wireless networks",
                icon: "wifi.square.fill",
                featureType: .wirelessAttacks
            ),
            PremiumFeature(
                name: "AI-Powered Prediction",
                description: "Predict potential vulnerabilities using machine learning",
                icon: "brain.head.profile",
                featureType: .aiPrediction
            ),
            PremiumFeature(
                name: "AR Network Visualization",
                description: "View your network topology in augmented reality",
                icon: "arkit",
                featureType: .arVisualization
            ),
            PremiumFeature(
                name: "Advanced Reports",
                description: "Generate detailed security reports with recommendations",
                icon: "doc.text.fill",
                featureType: .advancedReports
            )
        ]
    }
    
    private func setupSubscriptions() {
        subscriptions = [
            Subscription(
                name: "Monthly Premium",
                price: 9.99,
                period: "month",
                features: [.wirelessAttacks, .aiPrediction],
                productId: "com.scanner.premium.monthly"
            ),
            Subscription(
                name: "Annual Premium",
                price: 99.99,
                period: "year",
                features: [.wirelessAttacks, .aiPrediction, .arVisualization, .advancedReports],
                productId: "com.scanner.premium.annual"
            )
        ]
    }
    
    func purchase(_ subscription: Subscription) {
        isPurchasing = true
        
        // Simulate purchase process
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.isPurchasing = false
            // In a real app, this would handle StoreKit purchase flow
            NotificationCenter.default.post(
                name: .premiumFeaturesUpdated,
                object: subscription.features
            )
        }
    }
    
    func restore() {
        isPurchasing = true
        
        // Simulate restore process
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            self.isPurchasing = false
            self.showingError = true
            self.errorMessage = "No previous purchases found"
        }
    }
}

struct MonetizationView: View {
    @StateObject private var viewModel = MonetizationViewModel()
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    featuresSection
                    subscriptionsSection
                    restoreButton
                }
                .padding()
            }
            .navigationTitle("Premium Features")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .overlay {
                if viewModel.isPurchasing {
                    ProgressView("Processing...")
                        .padding()
                        .background(.regularMaterial)
                        .cornerRadius(8)
                }
            }
            .alert("Error", isPresented: $viewModel.showingError) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(viewModel.errorMessage)
            }
        }
    }
    
    private var featuresSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Premium Features")
                .font(.headline)
            
            ForEach(viewModel.features) { feature in
                HStack(spacing: 16) {
                    Image(systemName: feature.icon)
                        .font(.title2)
                        .foregroundColor(.blue)
                        .frame(width: 44, height: 44)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(feature.name)
                            .font(.subheadline)
                            .fontWeight(.semibold)
                        
                        Text(feature.description)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(12)
            }
        }
    }
    
    private var subscriptionsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Select Your Plan")
                .font(.headline)
            
            ForEach(viewModel.subscriptions) { subscription in
                VStack(spacing: 8) {
                    HStack {
                        VStack(alignment: .leading) {
                            Text(subscription.name)
                                .font(.title3)
                                .fontWeight(.semibold)
                            
                            Text("\(subscription.price, format: .currency(code: "USD"))/\(subscription.period)")
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        Button("Subscribe") {
                            viewModel.purchase(subscription)
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    
                    Divider()
                    
                    Text("Includes: ")
                        .font(.caption)
                        + Text(subscription.features.map { $0.description }.joined(separator: ", "))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(12)
            }
        }
    }
    
    private var restoreButton: some View {
        Button("Restore Purchases") {
            viewModel.restore()
        }
        .font(.footnote)
        .foregroundColor(.secondary)
    }
}

extension Notification.Name {
    static let premiumFeaturesUpdated = Notification.Name("premiumFeaturesUpdated")
}
